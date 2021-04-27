"""
Utility functions for dokflow document processing.
"""

import logging
from io import BytesIO

from pdf2image import convert_from_bytes

logger = logging.getLogger(__name__)


def generate_pdf_preview(file_field, max_pages: int = 1):
    """
    Generate a preview image from a PDF file.
    
    Converts the first page of a PDF document to a JPEG image for preview purposes.
    
    Args:
        file_field: Django FileField or file-like object containing PDF data
        max_pages: Maximum number of pages to process (default: 1)
        
    Returns:
        BytesIO: JPEG image buffer, or None if conversion fails
        
    Raises:
        IOError: If file cannot be read
        Exception: If pdf2image conversion fails
    """
    try:
        # Read file content
        if hasattr(file_field, 'read'):
            file_content = file_field.read()
            # Reset file pointer if seekable
            if hasattr(file_field, 'seek'):
                file_field.seek(0)
        else:
            file_content = file_field

        # Convert PDF to image
        images = convert_from_bytes(file_content, first_page=1, last_page=max_pages)
        
        if not images:
            logger.warning("PDF conversion returned no images")
            return None
        
        # Save first image to BytesIO buffer
        preview_buffer = BytesIO()
        images[0].save(preview_buffer, format='JPEG', quality=85)
        preview_buffer.seek(0)
        
        logger.debug(f"Successfully generated preview from PDF ({len(images)} pages)")
        return preview_buffer
        
    except Exception as e:
        logger.error(f"PDF preview generation failed: {str(e)}")
        raise
