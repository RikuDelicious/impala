import os

from .core import *

SETTINGS_MODULE_NAME = "impala.settings.devcontainer"

SECRET_KEY = "django-insecure-i3*kt5pcp^s0d1f--ql3@wk4_y$tdtbohof3kdv=kymzt!-yg="

DEBUG = True

ALLOWED_HOSTS = []

MIDDLEWARE += [
    "impala.middlewares.add_x_real_ip",
    "django_ratelimit.middleware.RatelimitMiddleware",
]

# Amazon S3 File Storage
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
AWS_STORAGE_BUCKET_NAME = "impala-localstack-public-bucket"  # localstack
AWS_S3_ENDPOINT_URL = "https://localhost.localstack.cloud:4566"  # localstack
AWS_QUERYSTRING_AUTH = False

# PostgreSQL
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["POSTGRES_DB_NAME"],
        "USER": os.environ["POSTGRES_USERNAME"],
        "PASSWORD": os.environ["POSTGRES_PASSWORD"],
        "HOST": os.environ["POSTGRES_HOSTNAME"],
        "PORT": os.environ["POSTGRES_PORT"],
    }
}

# Cache
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.memcached.PyLibMCCache",
        "LOCATION": os.environ["MEMCACHED_LOCATION"],
    }
}

# Django Ratelimit
# https://github.com/jsocol/django-ratelimit
RATELIMIT_ENABLE = True
RATELIMIT_VIEW = "api.views.ratelimited_error"
RATELIMIT_IP_META_KEY = "HTTP_X_REAL_IP"  # HTTPヘッダーはX-Real-Ip
