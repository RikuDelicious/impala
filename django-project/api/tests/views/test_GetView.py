from __future__ import annotations

import json
from unittest.mock import patch

import pytest
from api.image_processing import QueryError
from api.tests.stubs import ImageProfileStub
from django.urls import reverse

# Fixtures
########################################################################################


@pytest.fixture(scope="session")
def view_url() -> str:
    return reverse("api:get")


@pytest.fixture(scope="function")
def patch_services():
    with patch("api.views.GetView.image_processing_service", autospec=True) as ips:
        with patch("api.views.GetView.image_model_service", autospec=True) as ims:
            yield {"image_processing": ips, "image_model": ims}


# Tests
########################################################################################


def test_cache_exists(client, view_url: str, patch_services: dict):
    patch_services["image_processing"].create_profile.return_value = ImageProfileStub()
    patch_services["image_processing"].create_image.return_value = "/path/to/image.jpeg"
    patch_services[
        "image_model"
    ].get_cache_image_url.return_value = "http://example.com/cache.jpeg"
    patch_services[
        "image_model"
    ].upload_image.return_value = "http://example.com/uploaded.jpeg"

    res = client.get(view_url)

    patch_services["image_processing"].create_profile.assert_called()
    patch_services["image_processing"].create_image.assert_not_called()
    patch_services["image_model"].get_cache_image_url.assert_called()
    patch_services["image_model"].upload_image.assert_not_called()

    assert res.status_code == 302
    assert res.url == "http://example.com/cache.jpeg"


def test_cache_None(client, view_url: str, patch_services: dict):
    patch_services["image_processing"].create_profile.return_value = ImageProfileStub()
    patch_services["image_processing"].create_image.return_value = "/path/to/image.jpeg"
    patch_services["image_model"].get_cache_image_url.return_value = None
    patch_services[
        "image_model"
    ].upload_image.return_value = "http://example.com/uploaded.jpeg"

    res = client.get(view_url)

    patch_services["image_processing"].create_profile.assert_called()
    patch_services["image_processing"].create_image.assert_called()
    patch_services["image_model"].get_cache_image_url.assert_called()
    patch_services["image_model"].upload_image.assert_called()

    assert res.status_code == 302
    assert res.url == "http://example.com/uploaded.jpeg"


def test_create_profile_QueryError(client, view_url: str, patch_services: dict):
    patch_services["image_processing"].create_profile.return_value = ImageProfileStub()
    patch_services["image_processing"].create_image.return_value = "/path/to/image.jpeg"
    patch_services[
        "image_model"
    ].get_cache_image_url.return_value = "http://example.com/cache.jpeg"
    patch_services[
        "image_model"
    ].upload_image.return_value = "http://example.com/uploaded.jpeg"

    error_messages = {"field_1": ["error_message_1"], "field_2": ["error_message_2"]}
    query_error = QueryError(error_messages)
    patch_services["image_processing"].create_profile.side_effect = query_error

    res = client.get(view_url)

    patch_services["image_processing"].create_profile.assert_called()
    patch_services["image_processing"].create_image.assert_not_called()
    patch_services["image_model"].get_cache_image_url.assert_not_called()
    patch_services["image_model"].upload_image.assert_not_called()

    assert res.status_code == 400
    assert res.content == json.dumps(error_messages).encode("utf-8")


def test_create_profile_other_Exception(client, view_url: str, patch_services: dict):
    patch_services["image_processing"].create_profile.return_value = ImageProfileStub()
    patch_services["image_processing"].create_profile.side_effect = Exception
    patch_services["image_processing"].create_image.return_value = "/path/to/image.jpeg"
    patch_services[
        "image_model"
    ].get_cache_image_url.return_value = "http://example.com/cache.jpeg"
    patch_services[
        "image_model"
    ].upload_image.return_value = "http://example.com/uploaded.jpeg"

    with pytest.raises(Exception):
        client.get(view_url)
