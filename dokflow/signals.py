"""
Signal handlers for dokflow document lifecycle events.

Handles document protection and audit compliance.
"""

import logging

from django.db.models import ProtectedError
from django.utils import timezone
from django.utils.translation import gettext as _

from dokflow.settings import PROTECT_AFTER

logger = logging.getLogger(__name__)


def protect_documents(sender, instance, **kwargs):
    """
    Prevent deletion of documents after protection period.
    
    This signal handler enforces audit compliance by making documents immutable
    after PROTECT_AFTER duration. Once protected, documents can only be updated
    through the version control mechanism (Document.objects.replace()).
    
    Args:
        sender: The Document model class
        instance: The Document instance being deleted
        **kwargs: Additional signal arguments
        
    Raises:
        ProtectedError: If document is protected from deletion
    """
    time_since_creation = timezone.now() - instance.created_at
    
    if time_since_creation > PROTECT_AFTER:
        logger.warning(
            f"Attempted deletion of protected document {instance.pk} "
            f"(created: {instance.created_at})"
        )
        raise ProtectedError(
            instance,
            _("This document is protected from deletion for audit compliance. "
              "Create a new version using Document.objects.replace() if updates are needed.")
        )
