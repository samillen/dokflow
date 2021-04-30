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
 # Dokflow

Dokflow is a lightweight, production-oriented document management app for Django projects.

This repository contains the `dokflow` Django app used to manage documents with versioning,
audit trails, preview generation, and configuration options suitable for business applications.

**Highlights**

- Document versioning and immutable history
- Audit logging and optional protection/lock-after-period
- Automatic preview generation for PDFs
- Type-based document classification and simple API surface

## Requirements

- Python 3.8+
- Django 3.2 or 4.x

## Installation

Install from PyPI:

```bash
pip install django-dokflow
```

Or install from source for development:

```bash
git clone https://github.com/your-org/dokflow.git
cd dokflow
pip install -e .
```

## Quick start

1. Add `dokflow` to `INSTALLED_APPS` in your Django `settings.py`:

```python
INSTALLED_APPS = [
    # ...
    'dokflow',
]
```

2. (Optional) Configure behavior via settings:

```python
from datetime import timedelta

# Relative to MEDIA_ROOT
DOKFLOW_DOCUMENTS_DIR = 'documents/'
DOKFLOW_PREVIEW_DIR = 'previews/'

# Time until documents become protected (immutable)
DOKFLOW_PROTECT_AFTER = timedelta(days=1)

# Enable/disable automatic preview rendering
DOKFLOW_RENDER_PREVIEW = True
```

3. Run migrations:

```bash
python manage.py migrate dokflow
```

## Usage

Core API examples:

```python
from dokflow.models import Document, DocumentType

invoice = DocumentType.objects.create(name='Invoice')

doc = Document.objects.create(name='Invoice-2026-001', type=invoice, file=uploaded_file)

# Replace file and create a new version
new_doc = Document.objects.replace(doc, new_file)

# Iterate version chain
for version in new_doc.version_chain:
    print(version.pk, version.file.name)
```

Refer to the code docstrings for more detailed API surface and signal behaviour.

## Configuration options

- `DOKFLOW_DOCUMENTS_DIR` (str): Relative folder under `MEDIA_ROOT` for documents. Default: `'documents/'`.
- `DOKFLOW_PREVIEW_DIR` (str): Relative folder for preview images. Default: `'previews/'`.
- `DOKFLOW_PROTECT_AFTER` (timedelta): Time after creation when documents become protected. Default: `timedelta(days=1)`.
- `DOKFLOW_RENDER_PREVIEW` (bool): Enable preview generation. Default: `True`.

## Tests

Run the test suite from the repository root (uses pytest):

```bash
pytest -q
```

## Contributing

Contributions are welcome. Please follow these steps:

1. Fork the repository and create a feature branch.
2. Add tests for any new behavior.
3. Open a pull request describing your changes.

See `CONTRIBUTING.md` (if present) for more details.

## License

This project is licensed under the MIT License.

## Maintainer

samillen <samillen@users.noreply.github.com>

