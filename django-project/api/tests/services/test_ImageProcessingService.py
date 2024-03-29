from __future__ import annotations

import os
from tempfile import TemporaryDirectory
from unittest.mock import patch

import PIL.Image
import pytest
from django import forms
from django.http import QueryDict

from api.image_processing import ImageProfileAbstract, ImageProfileForm, QueryError
from api.services import ImageProcessingService

# Stubs
########################################################################################


class ImageProfileStub(ImageProfileAbstract):
    def __init__(self, quality: int | None):
        self._quality = quality

    def create_pil_image(self) -> PIL.Image.Image:
        return PIL.Image.new(mode="RGB", size=(512, 512), color=(100, 100, 100))

    @property
    def quality(self) -> int | None:
        return self._quality

    @property
    def upload_file_name(self) -> str:
        raise NotImplementedError()

    @classmethod
    def get_extension(cls) -> str:
        return "jpeg"

    def dump_signiture(self) -> str:
        raise NotImplementedError()


class ImageProfileFormStub(ImageProfileForm):
    intfield = forms.IntegerField()

    def get_profile(self) -> ImageProfileAbstract:
        return ImageProfileStub(quality=75)

    @classmethod
    def get_profile_type(self) -> str:
        return "jpeg_plain"


class ImageProfileFormStub2(ImageProfileForm):
    intfield = forms.IntegerField()

    def get_profile(self) -> ImageProfileAbstract:
        return ImageProfileStub(quality=75)

    @classmethod
    def get_profile_type(self) -> str:
        return "png_plain"


# Fixtures
########################################################################################


@pytest.fixture(scope="function")
def temp_dir():
    with TemporaryDirectory() as dir_name:
        yield dir_name


@pytest.fixture(scope="session")
def stub_form_classes():
    return [ImageProfileFormStub2, ImageProfileFormStub]


# Tests
########################################################################################

# ImageProcessingService.create_profile()


def test_create_profile_query_valid():
    form = ImageProfileFormStub({"intfield": 1})
    querydict = QueryDict()
    with patch.object(ImageProcessingService, "route_querydict", return_value=form):
        result = ImageProcessingService.create_profile(querydict)
        assert isinstance(result, ImageProfileStub)


def test_create_profile_query_invalid():
    form = ImageProfileFormStub({"intfield": "hoge"})
    querydict = QueryDict()
    with patch.object(ImageProcessingService, "route_querydict", return_value=form):
        with pytest.raises(QueryError) as exc_info:
            ImageProcessingService.create_profile(querydict)
        assert exc_info.value.messages == dict(form.errors)


# ImageProcessingService.route_querydict()


def test_route_querydict_form_routed(stub_form_classes):
    with patch.object(ImageProcessingService, "form_classes", stub_form_classes):
        querydict = QueryDict("a=1&profile_type=jpeg_plain&b=2")

        result = ImageProcessingService.route_querydict(querydict)
        assert isinstance(result, ImageProfileFormStub)


def test_route_querydict_form_not_routed(stub_form_classes):
    with patch.object(ImageProcessingService, "form_classes", stub_form_classes):
        querydict = QueryDict("a=1&profile_type=not_supported_type&b=2")

        with pytest.raises(QueryError) as exc_info:
            ImageProcessingService.route_querydict(querydict)
        error_message = "このフィールドには次のうちいずれかの値を入力してください。(png_plain, jpeg_plain)"
        assert exc_info.value.messages == {"profile_type": [error_message]}


def test_route_querydict_None(stub_form_classes):
    with patch.object(ImageProcessingService, "form_classes", stub_form_classes):
        querydict = QueryDict("a=1&b=2")

        with pytest.raises(QueryError) as exc_info:
            ImageProcessingService.route_querydict(querydict)

        error_message = "このフィールドは必須です"
        assert exc_info.value.messages == {"profile_type": [error_message]}


# ImageProcessingService.create_image()


def test_create_image_quality_None(temp_dir):
    result_image_path = ImageProcessingService.create_image(
        ImageProfileStub(quality=None), temp_dir
    )
    assert os.path.isfile(result_image_path)
    assert os.path.splitext(result_image_path)[1] == ".jpeg"


def test_create_image_quality_75(temp_dir):
    result_image_path = ImageProcessingService.create_image(
        ImageProfileStub(quality=75), temp_dir
    )
    assert os.path.isfile(result_image_path)
    assert os.path.splitext(result_image_path)[1] == ".jpeg"


def test_create_image_base_dir_not_exist():
    fake_dir = "/path/to/fake/dir"
    expected_error_message = "No such directory. base_dir: /path/to/fake/dir"
    with pytest.raises(FileNotFoundError, match=expected_error_message):
        ImageProcessingService.create_image(ImageProfileStub(quality=75), fake_dir)
