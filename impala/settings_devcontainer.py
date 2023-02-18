import os

from .settings import *

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