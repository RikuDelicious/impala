from __future__ import annotations

import os
from tempfile import TemporaryDirectory
from unittest.mock import PropertyMock, patch

import PIL.Image
import pytest
from django.core.files import File

from api.image_processing import ImageProfileAbstract
from api.models import Image
from api.services import ImageModelService

# Stubs
########################################################################################


class ImageProfileStub(ImageProfileAbstract):
    def create_pil_image(self) -> PIL.Image.Image:
        raise NotImplementedError()

    @property
    def quality(self) -> int | None:
        raise NotImplementedError()

    @property
    def upload_file_name(self) -> str:
        raise NotImplementedError()

    @classmethod
    def get_extension(cls) -> str:
        raise NotImplementedError()

    def dump_signiture(self) -> str:
        raise NotImplementedError()


# Fixtures
########################################################################################

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def setup_teardown_db(settings):
    settings.MEDIA_ROOT = settings.BASE_DIR / "media/"
    settings.MEDIA_URL = "media/"
    yield
    Image.objects.all().delete()


@pytest.fixture(scope="function")
def temp_dir():
    with TemporaryDirectory() as dir_name:
        yield dir_name


@pytest.fixture(scope="function")
def temp_image_path(temp_dir):
    pil_image = PIL.Image.new("RGB", (10, 10), (10, 10, 10))
    save_path = os.path.join(temp_dir, "temp.jpeg")
    pil_image.save(save_path)
    return save_path


@pytest.fixture(scope="function")
def existing_images(temp_dir):
    images = []
    for i in range(3):
        pil_image = PIL.Image.new("RGB", (10, 10), (10, 10, 10))
        save_path = os.path.join(temp_dir, f"existing_image_{i}.jpeg")
        pil_image.save(save_path)
        with open(save_path, "rb") as f:
            upload_file = File(f, name=f"existing_image_{i}.jpeg")
            image = Image.objects.create(
                upload=upload_file,
                profile_signiture=f"existing_image_profile_signiture_{i}",
            )
        images.append(image)

    return images


# Tests
########################################################################################


def test_get_cache_image_url_exists(existing_images):
    profile = ImageProfileStub()
    with patch.object(
        profile, "dump_signiture", return_value=existing_images[0].profile_signiture
    ):
        result = ImageModelService.get_cache_image_url(profile=profile)
        assert result == existing_images[0].upload.url


def test_get_cache_image_url_not_exists(existing_images):
    profile = ImageProfileStub()
    with patch.object(
        profile, "dump_signiture", return_value="new_image_profile_signiture"
    ):
        result = ImageModelService.get_cache_image_url(profile=profile)
        assert result is None


def test_upload_image(image_url_prefix, temp_image_path):
    with patch.object(
        ImageProfileStub,
        "upload_file_name",
        new_callable=PropertyMock(return_value="upload_image_file_name.jpeg"),
    ):
        profile = ImageProfileStub()
        with patch.object(
            profile, "dump_signiture", return_value="image_profile_signiture"
        ):
            result = ImageModelService.upload_image(temp_image_path, profile)

    expected_url = image_url_prefix + "upload_image_file_name.jpeg"
    assert result == expected_url
