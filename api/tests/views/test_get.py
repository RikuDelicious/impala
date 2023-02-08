from __future__ import annotations

import json
from unittest.mock import patch

import pytest
from django.http import QueryDict
from django.urls import reverse
from PIL.Image import Image

from api import container as api_container
from api import views
from api.containers import Container
from api.image_processing import ImageProfileAbstract, QueryError
from api.services import ImageModelServiceAbstract, ImageProcessingServiceAbstract

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


class ImageProcessingServiceStub(ImageProcessingServiceAbstract):
    def create_profile(self, querydict: QueryDict) -> ImageProfileAbstract:
        return ImageProfileStub()

    def create_image(self, profile: ImageProfileAbstract, base_dir: str) -> str:
        return "/path/to/image.jpeg"


class ImageModelServiceStub(ImageModelServiceAbstract):
    def get_cache_image_url(self, profile: ImageProfileAbstract) -> str | None:
        return "http://example.com/cache.jpeg"

    def upload_image(self, image_path: str) -> str:
        return "http://example.com/uploaded.jpeg"


# Fixtures
########################################################################################


@pytest.fixture
def view_url() -> str:
    return reverse("api:get")


@pytest.fixture
def container() -> Container:
    return api_container


# Tests
########################################################################################


def test_cache_exists(rf, view_url: str, container: Container):
    image_processing = ImageProcessingServiceStub()
    image_model = ImageModelServiceStub()

    with container.image_processing_service.override(image_processing):
        with container.image_model_service.override(image_model):
            req = rf.get(view_url)
            res = views.get(req)

            assert res.status_code == 302
            assert res.url == "http://example.com/cache.jpeg"


def test_cache_None(rf, view_url: str, container: Container):
    image_processing = ImageProcessingServiceStub()
    image_model = ImageModelServiceStub()

    with patch.object(image_model, "get_cache_image_url", return_value=None):
        with container.image_processing_service.override(image_processing):
            with container.image_model_service.override(image_model):
                req = rf.get(view_url)
                res = views.get(req)

                assert res.status_code == 302
                assert res.url == "http://example.com/uploaded.jpeg"


def test_create_profile_QueryError(rf, view_url: str, container: Container):
    image_processing = ImageProcessingServiceStub()
    image_model = ImageModelServiceStub()
    error_messages = {"field_1": ["error_message_1"], "field_2": ["error_message_2"]}
    query_error = QueryError(error_messages)

    with patch.object(image_processing, "create_profile", side_effect=query_error):
        with container.image_processing_service.override(image_processing):
            with container.image_model_service.override(image_model):
                req = rf.get(view_url)
                res = views.get(req)

                assert res.status_code == 400
                assert res.content == json.dumps(error_messages).encode("utf-8")


def test_create_profile_other_Exception(rf, view_url: str, container: Container):
    image_processing = ImageProcessingServiceStub()
    image_model = ImageModelServiceStub()
    with patch.object(image_processing, "create_profile", side_effect=Exception):
        with container.image_processing_service.override(image_processing):
            with container.image_model_service.override(image_model):
                with pytest.raises(Exception):
                    req = rf.get(view_url)
                    views.get(req)
