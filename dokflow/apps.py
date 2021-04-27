"""
Django app configuration for dokflow.
"""

import logging

from django.apps import AppConfig
from django.db.models.signals import pre_delete

from dokflow.settings import LOGGING_LEVEL

logger = logging.getLogger(__name__)
logger.setLevel(LOGGING_LEVEL)


class DokflowConfig(AppConfig):
    """Configuration for the dokflow document management application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dokflow"
    verbose_name = "Dokflow - Document Management"

    def ready(self):
        """
        Django app initialization.
        
        Connects signal handlers for document lifecycle events.
        """
        from dokflow.signals import protect_documents

        pre_delete.connect(
            protect_documents,
            sender="dokflow.Document",
            dispatch_uid="dokflow_protect_documents",
        )
        logger.info("Dokflow app initialized and signals connected")
