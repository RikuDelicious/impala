from .core import *

SETTINGS_MODULE_NAME = "impala.settings.local"

SECRET_KEY = "django-insecure-i3*kt5pcp^s0d1f--ql3@wk4_y$tdtbohof3kdv=kymzt!-yg="

DEBUG = True

ALLOWED_HOSTS = []

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

MEDIA_ROOT = BASE_DIR / "media/"
MEDIA_URL = "media/"

# Django Ratelimit
# https://github.com/jsocol/django-ratelimit
RATELIMIT_ENABLE = False
