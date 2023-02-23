from __future__ import annotations

import json
import time
from unittest.mock import patch

import PIL.Image
import pytest
from django.conf import settings
from django.core.cache import cache
from django.test import Client
from django.urls import reverse

from api.image_processing import ImageProfileAbstract

# テスト用のIPアドレス (RFC5737)
# 192.0.2.0/24 (TEST-NET-1)
# 198.51.100.0/24 (TEST-NET-2)
# 203.0.113.0/24 (TEST-NET-3)

if settings.SETTINGS_MODULE_NAME == "impala.settings.local":
    pytest.skip("skipping ratelimit tests", allow_module_level=True)

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
    """
    django-ratelimitによるレート制限が掛かるまでのリクエスト回数にブレがある。
    そのため、きっかり (レート制限 + 1) 回目に制限が掛かることの検証は出来ない。
    原因が不明で対処できないため、レート制限回数の2倍の回数までに制限が掛かれば許容とする。
    """
    for request_count in range(1, rate_per_second * 2 + 1):
        response = client.get(reverse("api:get"), HTTP_X_REAL_IP="192.0.2.5")

        if response.status_code == 429 and request_count <= rate_per_second:
            pytest.fail("想定外の箇所でリクエストレート制限に掛かりました")
        if response.status_code == 429 and request_count > rate_per_second:
            assert response.status_code == 429
            assert json.loads(response.content) == {"error": "ratelimited"}
            break
        if request_count == rate_per_second * 2 and response.status_code != 429:
            pytest.fail("リクエストレート制限に掛かりませんでした。")


def test_ratelimit_key_ip(client: Client, rate_per_second: int):
    for request_count in range(1, rate_per_second * 2 + 1):
        # 確実にレート制限を掛けるため、制限の2倍の回数までリクエストしておく
        response = client.get(reverse("api:get"), HTTP_X_REAL_IP="192.0.2.5")
        if response.status_code == 429:
            break
        if request_count == rate_per_second * 2 and response.status_code != 429:
            pytest.fail("想定した箇所でリクエストレート制限に掛かりませんでした。")

    # 他のipからのリクエストは制限に掛かっていないことを確認する
    other_ip_response = client.get(reverse("api:get"), HTTP_X_REAL_IP="192.0.2.6")

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
    尚、django-ratelimitによるレート制限が掛かるまでのリクエスト回数にはブレがあるため、
    レート制限の2倍の回数までにアクセス制限が掛かればOKとする。
    """
    count = 1
    while count <= rate_per_minute * 2:
        # 1秒間のレート制限限界までまとめてリクエストする
        for i in range(rate_per_second):
            response = client.get(reverse("api:get"), HTTP_X_REAL_IP="192.0.2.5")

            # 1回のリクエスト毎のレスポンスステータス確認
            if response.status_code == 429 and count <= rate_per_minute:
                pytest.fail("想定外の箇所でリクエストレート制限に掛かりました")
            if response.status_code == 429 and count > rate_per_minute:
                assert response.status_code == 429
                assert json.loads(response.content) == {"error": "ratelimited"}
                # while ループから抜ける
                count = rate_per_minute * 2 + 1
                break

            # rate_per_minute * 2 回までリクエストした場合
            # ここではresponse.status_code != 429のため、テスト失敗
            if count == rate_per_minute * 2 and response.status_code != 429:
                pytest.fail("リクエストレート制限に掛かりませんでした。")

            # count変数で次のリクエスト回数を保持
            count += 1

        # 1秒間のレート制限に掛からないように1.1秒間止まる
        time.sleep(1.1)
