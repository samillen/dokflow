"""
Configuration settings for dokflow application.

All settings can be customized in the Django project's settings.py file
by setting the corresponding DOKFLOW_* variable.
"""

from datetime import timedelta
from django.conf import settings


# Document storage configuration
DOCUMENTS_DIR = getattr(
    settings,
    "DOKFLOW_DOCUMENTS_DIR",
    "documents/",
    help_text="Directory for storing documents within MEDIA_ROOT"
)

PREVIEW_DIR = getattr(
    settings,
    "DOKFLOW_PREVIEW_DIR",
    "preview/",
    help_text="Directory for storing preview images within MEDIA_ROOT"
)

# Document protection configuration
PROTECT_AFTER = getattr(
    settings,
    "DOKFLOW_PROTECT_AFTER",
    timedelta(days=1),
    help_text="Duration after which documents become protected from deletion"
)

# Preview generation configuration
RENDER_PREVIEW = getattr(
    settings,
    "DOKFLOW_RENDER_PREVIEW",
    True,
    help_text="Enable automatic preview generation for PDF documents"
)

# Logging configuration
LOGGING_LEVEL = getattr(
    settings,
    "DOKFLOW_LOGGING_LEVEL",
    "INFO",
    help_text="Log level for dokflow logger (DEBUG, INFO, WARNING, ERROR)"
)
