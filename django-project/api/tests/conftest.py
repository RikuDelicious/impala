import os
from urllib.parse import urljoin

import pytest

from api import models


@pytest.fixture
def image_url_prefix(settings) -> str:
    upload_to = models.Image._meta.get_field("upload").upload_to
    if settings.SETTINGS_MODULE_NAME == "impala.settings.local":
        base = settings.MEDIA_URL
        return os.path.join(base, upload_to)
    elif settings.SETTINGS_MODULE_NAME == "impala.settings.devcontainer":
        url_path = os.path.join(settings.AWS_STORAGE_BUCKET_NAME, upload_to)
        return urljoin(settings.AWS_S3_ENDPOINT_URL, url_path)
    else:
        pytest.exit("settings_module_name is wrong.")
