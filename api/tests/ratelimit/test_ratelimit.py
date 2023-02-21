from __future__ import annotations

import json
import time
from unittest.mock import patch

import PIL.Image
import pytest
from django.core.cache import cache
from django.test import Client
from django.urls import reverse

from api.image_processing import ImageProfileAbstract

# テスト用のIPアドレス (RFC5737)
# 192.0.2.0/24 (TEST-NET-1)
# 198.51.100.0/24 (TEST-NET-2)
# 203.0.113.0/24 (TEST-NET-3)

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


@pytest.fixture(autouse=True)
def patch_services():
    """
    画像処理・データベース操作を行う処理を全てモックにしてテスト時の処理負荷を軽減する
    """
    with patch("api.views.GetView.image_processing_service", autospec=True) as ips:
        with patch("api.views.GetView.image_model_service", autospec=True) as ims:
            ips.create_profile.return_value = ImageProfileStub()
            ips.create_image.return_value = "image_path"
            ims.get_cache_image_url.return_value = "https://example.com/cache_image_url"
            ims.upload_image.return_value = "https://example.com/uploaded_image_url"
            yield


@pytest.fixture(autouse=True)
def clear_cache():
    """
    レート制限処理がキャッシュに依存しているため、
    テスト関数毎にキャッシュを全て削除する。
    """
    yield
    cache.clear()


@pytest.fixture
def rate_per_second() -> int:
    return 50


@pytest.fixture
def rate_per_minute() -> int:
    return 500


# Tests
########################################################################################


def test_ratelimit_not_exceed(client: Client, rate_per_second: int):
    for i in range(rate_per_second):
        response = client.get(reverse("api:get"), HTTP_X_REAL_IP="192.0.2.5")
        if response.status_code == 429:
            pytest.fail("リクエストレート制限に掛かりました")


def test_ratelimit_exceed(client: Client, rate_per_second: int):
    for i in range(rate_per_second):
        response = client.get(reverse("api:get"), HTTP_X_REAL_IP="192.0.2.5")
        if response.status_code == 429:
            pytest.fail("想定外の箇所でリクエストレート制限に掛かりました")
    response = client.get(reverse("api:get"), HTTP_X_REAL_IP="192.0.2.5")
    assert response.status_code == 429
    assert json.loads(response.content) == {"error": "ratelimited"}


def test_ratelimit_key_ip(client: Client, rate_per_second: int):
    for i in range(rate_per_second):
        response = client.get(reverse("api:get"), HTTP_X_REAL_IP="192.0.2.5")
        if response.status_code == 429:
            pytest.fail("想定外の箇所でリクエストレート制限に掛かりました")
    ratelimited_ip_response = client.get(reverse("api:get"), HTTP_X_REAL_IP="192.0.2.5")
    other_ip_response = client.get(reverse("api:get"), HTTP_X_REAL_IP="192.0.2.6")

    assert ratelimited_ip_response.status_code == 429
    assert other_ip_response.status_code != 429


def test_ratelimit_per_minute_not_exceed(
    client: Client, rate_per_second: int, rate_per_minute: int
):
    """
    1秒間のレート制限に掛からないリクエストレートで、
    1分以内でレート制限までリクエストできることを確認する
    """
    count = 0
    while count < rate_per_minute:
        for i in range(rate_per_second):
            """
            1秒間のレート制限限界までリクエストする
            """
            response = client.get(reverse("api:get"), HTTP_X_REAL_IP="192.0.2.5")
            if response.status_code == 429:
                pytest.fail("リクエストレート制限に掛かりました")
            count += 1
            if count == rate_per_minute:
                break
        # 1秒間のレート制限に掛からないように1.1秒間止まる
        time.sleep(1.1)


def test_ratelimit_per_minute_exceed(
    client: Client, rate_per_second: int, rate_per_minute: int
):
    """
    1秒間のレート制限に掛からないリクエストレートで、
    1分以内にレート制限を越えるリクエストを行うとアクセス制限されることを確認する
    """
    count = 0
    while count < rate_per_minute:
        for i in range(rate_per_second):
            """
            1秒間のレート制限限界までリクエストする
            ここではレート制限に掛からない
            """
            response = client.get(reverse("api:get"), HTTP_X_REAL_IP="192.0.2.5")
            if response.status_code == 429:
                pytest.fail("想定外の箇所でリクエストレート制限に掛かりました")
            count += 1
            if count == rate_per_minute:
                break
        # 1秒間のレート制限に掛からないように1.1秒間止まる
        time.sleep(1.1)

    response = client.get(reverse("api:get"), HTTP_X_REAL_IP="192.0.2.5")
    assert response.status_code == 429
