import tempfile

USE_TZ = False
SECRET_KEY = "fake_key_for_testing"
INSTALLED_APPS = [
    "dokflow",
    "tests",
]
MEDIA_ROOT = tempfile.mkdtemp(prefix="dokflow_test")
DATABASES = dict(
    default=dict(
        ENGINE="django.db.backends.sqlite3",
        NAME=":memory:",
    )
)
