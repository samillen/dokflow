# Dokflow

**Dokflow** is a production-grade document management system for Django applications.
It provides comprehensive document handling with versioning, audit trails, and automatic preview generation.

## Overview

Dokflow is designed for modern business and accounting applications that require robust document management without deploying a full Document Management System like Mayan EDMS.

## Key Features

* **Document Versioning**: Automatic version control through document replacement mechanism
* **Audit Trail Compliance**: Documents become read-only after protection period for compliance
* **Automatic Previews**: PDF-to-JPEG preview generation with error handling
* **Type Classification**: Organize documents using document types
* **Immutability**: Once created, documents cannot be modified - only versioned
* **Transaction Safety**: Atomic operations for document creation and replacement
* **Comprehensive Logging**: Full audit logging for document lifecycle events
* **Database Optimization**: Indexed queries for performance

## Architecture Highlights

* Clean separation of concerns (models, signals, utilities)
* Comprehensive docstrings and type hints for maintainability
* Error handling with graceful fallbacks
* Property-based API for document relationships
* Production-ready signal handling and lifecycle management

## Compatibility

Tested with the following versions:

* Django: 3.2, 4.0+
* Python: 3.8, 3.9, 3.10, 3.11

## Installation

Install `django-dokflow` using pip:

```bash
pip install django-dokflow
```

## Quick Start

1. Add "dokflow" to your INSTALLED_APPS:

```python
INSTALLED_APPS = [
    ...
    "dokflow",
]
```

2. Configure in your project's settings.py (optional):

```python
# Document storage paths (relative to MEDIA_ROOT)
DOKFLOW_DOCUMENTS_DIR = "documents/"
DOKFLOW_PREVIEW_DIR = "preview/"

# Document protection duration
from datetime import timedelta
DOKFLOW_PROTECT_AFTER = timedelta(days=1)

# Enable/disable preview generation
DOKFLOW_RENDER_PREVIEW = True
```

3. Run migrations:

```bash
python manage.py migrate dokflow
```

## Usage Example

```python
from dokflow.models import Document, DocumentType

# Create a document type
invoice_type = DocumentType.objects.create(name="Invoice")

# Create a document
doc = Document.objects.create(
    name="Invoice-2024-001",
    type=invoice_type,
    file=uploaded_file
)

# Create a new version
updated_doc = Document.objects.replace(doc, updated_file)

# Access version chain
print(updated_doc.version_chain)  # [original_doc, updated_doc]
```

## Configuration

Customize dokflow behavior in your Django settings:

| Setting | Default | Description |
|---------|---------|-------------|
| `DOKFLOW_DOCUMENTS_DIR` | `"documents/"` | Document storage directory |
| `DOKFLOW_PREVIEW_DIR` | `"preview/"` | Preview image storage directory |
| `DOKFLOW_PROTECT_AFTER` | `timedelta(days=1)` | Duration until documents become protected |
| `DOKFLOW_RENDER_PREVIEW` | `True` | Enable automatic PDF preview generation |

## License

MIT

## Authors

* samillen <samillen@users.noreply.github.com>

## Original Project

Based on the original django-doma by Florian Rämisch
