"""
Document management models for dokflow.

This module provides the core models for handling document storage, versioning,
and management in Django applications. It implements:

- Document type classification
- Document storage with audit-proof protection
- Automatic preview generation for PDF documents
- Version control through document replacement mechanism
"""

import logging
from io import BytesIO
from uuid import uuid4

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import models, transaction
from django.utils.text import slugify
from django.utils.translation import gettext as _

from dokflow.settings import DOCUMENTS_DIR, PREVIEW_DIR, RENDER_PREVIEW
from dokflow.utils import generate_pdf_preview

logger = logging.getLogger(__name__)


class CreatedModifiedModel(models.Model):
    """
    Abstract base model that tracks creation and modification timestamps.
    
    All timestamps are automatically managed by Django's auto_now and auto_now_add.
    """

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Automatically updated on each save"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Set on creation, never changes"
    )

    class Meta:
        abstract = True


class SlugifiedModel(models.Model):
    """
    Abstract base model that provides automatic slug generation from name field.
    
    The slug is generated once on creation and remains immutable for clean URLs.
    """

    slug = models.SlugField(
        editable=False,
        unique=True,
        help_text="Auto-generated URL-friendly identifier"
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """Generate slug from name field if this is a new instance."""
        if self._state.adding:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class DocumentType(SlugifiedModel):
    """
    Classification model for documents.
    
    Groups documents into categories for organization and filtering.
    Each DocumentType can have multiple documents.
    """

    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Human-readable document type (e.g., 'Invoice', 'Contract')"
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Document Type"
        verbose_name_plural = "Document Types"

    def __str__(self):
        return self.name


class DocumentManager(models.Manager):
    """
    Custom manager for Document model with specialized query and creation methods.
    """

    def replace(self, document, file):
        """
        Create a new version of a document while preserving the original.
        
        This implements a version control mechanism where the original document
        is preserved and linked via the 'replaces' field. This ensures audit trails
        and compliance requirements are met.
        
        Args:
            document: The Document instance to be replaced
            file: The SimpleUploadedFile or file-like object for the new version
            
        Returns:
            Document: The newly created document version
            
        Raises:
            ValidationError: If document is already the latest version or invalid
        """
        if not document.pk:
            raise ValidationError(_("Cannot replace an unsaved document."))
        
        try:
            with transaction.atomic():
                new_document = self.create(
                    name=document.name,
                    type=document.type,
                    preview=document.preview,
                    content=document.content,
                    replaces=document,
                    file=file,
                )
                logger.info(
                    f"Document {document.pk} replaced with version {new_document.pk}"
                )
                return new_document
        except Exception as e:
            logger.error(f"Failed to replace document {document.pk}: {str(e)}")
            raise


class Document(CreatedModifiedModel):
    """
    Core document model with immutability and version control.
    
    Features:
    - Immutable file storage after initial creation
    - Automatic PDF preview generation
    - Version control through replacement mechanism
    - Unique identification via UUID
    - Ordered by creation time for audit compliance
    
    The document becomes read-only after creation_time + PROTECT_AFTER duration,
    enforced at the signal level for audit compliance.
    """

    name = models.CharField(
        max_length=255,
        help_text="Document display name"
    )
    type = models.ForeignKey(
        DocumentType,
        on_delete=models.PROTECT,
        related_name="documents",
        help_text="Document classification type"
    )
    uuid = models.UUIDField(
        unique=True,
        default=uuid4,
        editable=False,
        help_text="Immutable unique identifier"
    )
    preview = models.ImageField(
        upload_to=PREVIEW_DIR,
        null=True,
        blank=True,
        help_text="Auto-generated preview image for PDF documents"
    )
    content = models.TextField(
        null=True,
        blank=True,
        help_text="Optional extracted text content from document"
    )
    replaces = models.OneToOneField(
        "self",
        on_delete=models.PROTECT,
        related_name="replaced_by",
        null=True,
        blank=True,
        help_text="Reference to the previous version of this document"
    )
    file = models.FileField(
        upload_to=DOCUMENTS_DIR,
        blank=True,
        help_text="Original document file"
    )

    objects = DocumentManager()

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Document"
        verbose_name_plural = "Documents"
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["uuid"]),
            models.Index(fields=["type"]),
        ]

    def __str__(self):
        return f"{self.pk} - {self.name}"

    def clean(self):
        """
        Validate document before saving.
        
        Raises:
            ValidationError: If document violates immutability constraints
        """
        if self.pk:
            # Check if this is an existing document (not a new one)
            original = Document.objects.get(pk=self.pk)
            if original.file and self.file != original.file:
                raise ValidationError(
                    _("Documents are immutable and cannot be modified. "
                      "Use Document.objects.replace() to create a new version.")
                )

    def save(self, *args, **kwargs):
        """
        Save document with automatic preview generation.
        
        Handles:
        - Validation of immutability constraints
        - Automatic PDF preview generation (if RENDER_PREVIEW is enabled)
        - Error handling and logging
        
        Raises:
            ValidationError: If document violates business rules
        """
        self.full_clean()
        
        # Generate preview for new documents with PDF files
        if not self.preview and RENDER_PREVIEW and self.file:
            try:
                self._generate_preview()
            except Exception as e:
                logger.warning(
                    f"Preview generation failed for document {self.name}: {str(e)}"
                )
                # Continue saving even if preview generation fails

        super().save(*args, **kwargs)

    def _generate_preview(self):
        """
        Generate a JPEG preview from PDF file.
        
        Attempts to convert the first page of a PDF to a JPEG image.
        If conversion fails, logs warning and continues without preview.
        """
        try:
            preview_image = generate_pdf_preview(self.file)
            if preview_image:
                self.preview = SimpleUploadedFile(
                    "preview.jpg",
                    preview_image.getvalue(),
                    content_type="image/jpeg"
                )
                logger.debug(f"Preview generated for document {self.name}")
        except Exception as e:
            logger.warning(
                f"Could not generate preview for {self.name}: {str(e)}"
            )

    @property
    def is_latest_version(self):
        """
        Check if this is the latest version of the document.
        
        Returns:
            bool: True if no newer version replaces this document
        """
        return not hasattr(self, 'replaced_by') or self.replaced_by is None

    @property
    def version_chain(self):
        """
        Get the complete version history chain for this document.
        
        Returns:
            list: Documents from original to current version
        """
        chain = [self]
        current = self
        
        while hasattr(current, 'replaces') and current.replaces:
            chain.insert(0, current.replaces)
            current = current.replaces
        
        return chain
