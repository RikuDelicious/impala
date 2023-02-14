from __future__ import annotations

import os
from tempfile import TemporaryDirectory

import pytest

from api.image_processing import (
    ColorRGB,
    ImageProfileAbstract,
    JPEGPlainProfile,
    PNGPlainProfile,
)
from api.models import Image
from api.services import ImageModelService

# Fixtures
########################################################################################

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def setup_teardown_db(settings):
    settings.MEDIA_ROOT = settings.BASE_DIR / "media/"
    settings.MEDIA_URL = "media/"
    yield
    Image.objects.all().delete()


@pytest.fixture(
    params=[
        JPEGPlainProfile(
            width=11, height=12, color_rgb=ColorRGB(143, 99, 196), quality=70
        ),
        PNGPlainProfile(
            width=9, height=10, color_rgb=ColorRGB(83, 183, 128), alpha=189
        ),
    ]
)
def sample_profile(request):
    return request.param


# Tests
########################################################################################


def test_get_cache_image_url_exists(settings, sample_profile: ImageProfileAbstract):
    with TemporaryDirectory() as temp_dir:
        pil_image = sample_profile.create_pil_image()
        temp_image_path = os.path.join(
            temp_dir, f"temp.{sample_profile.get_extension()}"
        )
        pil_image.save(temp_image_path)

        ImageModelService.upload_image(temp_image_path, sample_profile)

    expected_url = os.path.join(
        settings.MEDIA_URL,
        "images/",
        sample_profile.upload_file_name,
    )

    result = ImageModelService.get_cache_image_url(profile=sample_profile)

    assert result == expected_url


def test_get_cache_image_url_not_exists(sample_profile: ImageProfileAbstract):
    result = ImageModelService.get_cache_image_url(profile=sample_profile)
    assert result is None


def test_upload_image(settings, sample_profile: ImageProfileAbstract):
    with TemporaryDirectory() as temp_dir:
        pil_image = sample_profile.create_pil_image()
        temp_image_path = os.path.join(
            temp_dir, f"temp.{sample_profile.get_extension()}"
        )
        pil_image.save(temp_image_path)

        result = ImageModelService.upload_image(temp_image_path, sample_profile)

    expected_url = os.path.join(
        settings.MEDIA_URL,
        "images/",
        sample_profile.upload_file_name,
    )
    assert result == expected_url
