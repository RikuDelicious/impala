from __future__ import annotations

from unittest.mock import patch

import pytest
from django import forms
from django.http import QueryDict
from PIL.Image import Image

from api.image_processing import ImageProfileAbstract, ImageProfileForm, QueryError
from api.services import ImageProcessingService

# Stubs
########################################################################################


class ImageProfileStub(ImageProfileAbstract):
    def create_pil_image(self) -> Image:
        raise NotImplementedError()

    @property
    def quality(self) -> int | None:
        raise NotImplementedError()

    @quality.setter
    def quality(self, value: int):
        raise NotImplementedError()

    @classmethod
    def get_extension(cls) -> str:
        raise NotImplementedError()


class ImageProfileFormStub(ImageProfileForm):
    intfield = forms.IntegerField()

    def get_profile(self) -> ImageProfileAbstract:
        return ImageProfileStub()

    @classmethod
    def get_profile_type(self) -> str:
        return "jpeg_plain"


class ImageProfileFormStub2(ImageProfileForm):
    intfield = forms.IntegerField()

    def get_profile(self) -> ImageProfileAbstract:
        return ImageProfileStub()

    @classmethod
    def get_profile_type(self) -> str:
        return "png_plain"


# Tests
########################################################################################

# ImageProcessingService.create_profile()


def test_create_profile_query_valid():
    service = ImageProcessingService()
    form = ImageProfileFormStub({"intfield": 1})
    querydict = QueryDict()
    with patch.object(service, "route_querydict", return_value=form):
        result = service.create_profile(querydict)
        assert isinstance(result, ImageProfileStub)


def test_create_profile_query_invalid():
    service = ImageProcessingService()
    form = ImageProfileFormStub({"intfield": "hoge"})
    querydict = QueryDict()
    with patch.object(service, "route_querydict", return_value=form):
        with pytest.raises(QueryError) as exc_info:
            service.create_profile(querydict)
        assert exc_info.value.messages == dict(form.errors)


# ImageProcessingService.route_querydict()


def test_route_querydict_form_routed():
    service = ImageProcessingService()
    service.form_classes = [ImageProfileFormStub2, ImageProfileFormStub]
    querydict = QueryDict("a=1&profile_type=jpeg_plain&b=2")

    result = service.route_querydict(querydict)
    assert isinstance(result, ImageProfileFormStub)


def test_route_querydict_form_not_routed():
    service = ImageProcessingService()
    service.form_classes = [ImageProfileFormStub2, ImageProfileFormStub]
    querydict = QueryDict("a=1&profile_type=not_supported_type&b=2")

    with pytest.raises(QueryError) as exc_info:
        service.route_querydict(querydict)
    error_message = 'このフィールドには次のうちいずれかの値を入力してください。("png_plain", "jpeg_plain")'
    assert exc_info.value.messages == {"profile_type": [error_message]}


def test_route_querydict_None():
    service = ImageProcessingService()
    service.form_classes = [ImageProfileFormStub2, ImageProfileFormStub]
    querydict = QueryDict("a=1&b=2")

    with pytest.raises(QueryError) as exc_info:
        service.route_querydict(querydict)

    error_message = "このフィールドは必須です"
    assert exc_info.value.messages == {"profile_type": [error_message]}


# ImageProcessingService.create_image()
