from __future__ import annotations

import os

import pytest
from django.urls import reverse

from api.image_processing import ColorRGB, JPEGPlainProfile, PNGPlainProfile
from api.models import Image

# Fixtures
########################################################################################

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def setup_teardown_db(settings):
    settings.MEDIA_ROOT = settings.BASE_DIR / "media/"
    settings.MEDIA_URL = "media/"
    yield
    Image.objects.all().delete()


@pytest.fixture(scope="session")
def view_url() -> str:
    return reverse("api:get")


@pytest.fixture(
    params=[
        {
            "query": "profile_type=jpeg_plain&width=10&height=10&color_rgb=BEF0CB&quality=68",
            "profile": JPEGPlainProfile(
                width=10, height=10, color_rgb=ColorRGB(190, 240, 203), quality=68
            ),
        },
        {
            "query": "profile_type=png_plain&width=10&height=10&color_rgb=BEF0CB&alpha=150",
            "profile": PNGPlainProfile(
                width=10, height=10, color_rgb=ColorRGB(190, 240, 203), alpha=150
            ),
        },
    ]
)
def valid_request_data(image_url_prefix, request):
    data = request.param.copy()
    data["expected_image_url"] = image_url_prefix + data["profile"].upload_file_name
    return data


@pytest.fixture(
    params=[
        "profile_type=jpeg_plain&width=hoge&height=10&color_rgb=BEF0CB&quality=68",
        "profile_type=png_plain&width=10&height=hoge&color_rgb=BEF0CB&quality=68",
        "profile_type=not_supported&width=10&height=10&color_rgb=BEF0CB&quality=68",
        "width=10&height=10&color_rgb=BEF0CB&quality=68",
    ]
)
def invalid_query(request) -> str:
    return request.param


# Tests
########################################################################################


def test_cache_exists(client, view_url: str, valid_request_data: dict):
    url = f"{view_url}?{valid_request_data['query']}"
    client.get(url)
    res = client.get(url)

    assert res.status_code == 302
    assert res.url == valid_request_data["expected_image_url"]


def test_cache_None(client, view_url: str, valid_request_data: dict):
    url = f"{view_url}?{valid_request_data['query']}"
    res = client.get(url)

    assert res.status_code == 302
    assert res.url == valid_request_data["expected_image_url"]


def test_create_profile_QueryError(capsys, client, view_url: str, invalid_query):
    with capsys.disabled():
        url = f"{view_url}?{invalid_query}"
        res = client.get(url)
        assert res.status_code == 400

        # エラーコンテンツの確認
        print()
        print(res.content.decode("utf-8"))
