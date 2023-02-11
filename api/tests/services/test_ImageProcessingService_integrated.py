from __future__ import annotations

import os
from tempfile import TemporaryDirectory

import pytest
from django.http import QueryDict

from api.image_processing import (
    ColorRGB,
    JPEGPlainProfile,
    JPEGPlainProfileForm,
    PNGPlainProfile,
    PNGPlainProfileForm,
    QueryError,
)
from api.services import ImageProcessingService

# Fixtures
########################################################################################


@pytest.fixture(scope="function")
def temp_dir():
    with TemporaryDirectory() as dir_name:
        yield dir_name


@pytest.fixture(
    params=[
        {
            "profile_class": JPEGPlainProfile,
            "profile_form_class": JPEGPlainProfileForm,
            "query": "profile_type=jpeg_plain&width=512&height=1024&color_rgb=B5F1CC&quality=63",
        },
        {
            "profile_class": PNGPlainProfile,
            "profile_form_class": PNGPlainProfileForm,
            "query": "profile_type=png_plain&width=320&height=960&color_rgb=F99417&alpha=200",
        },
    ]
)
def valid_query(request):
    """
    各プロファイルクラスに対応する正しいクエリ文字列を返すフィクスチャ
    """
    return request.param


@pytest.fixture(
    params=[
        {
            "profile_class": None,
            "profile_form_class": None,
            "query": "profile_type=hogehoge&width=512&height=1024&color_rgb=B5F1CC&quality=63",
        },
        {
            "profile_class": JPEGPlainProfile,
            "profile_form_class": JPEGPlainProfileForm,
            "query": "profile_type=jpeg_plain&width=hoge&height=1024&color_rgb=B5F1CC&quality=63",
        },
        {
            "profile_class": PNGPlainProfile,
            "profile_form_class": PNGPlainProfileForm,
            "query": "profile_type=png_plain&width=320&height=hoge&color_rgb=F99417&alpha=200",
        },
    ]
)
def invalid_query(request):
    """
    未対応のprofile_type、
    及び各プロファイルクラスに対応する正しくないクエリ文字列を返すフィクスチャ
    """
    return request.param


# Tests
########################################################################################

# ImageProcessingService.create_profile()


def test_create_profile_query_valid(valid_query):
    service = ImageProcessingService()
    result = service.create_profile(QueryDict(valid_query["query"]))
    assert isinstance(result, valid_query["profile_class"])


def test_create_profile_query_invalid(invalid_query):
    service = ImageProcessingService()
    with pytest.raises(QueryError):
        service.create_profile(QueryDict(invalid_query["query"]))


# ImageProcessingService.route_querydict()


def test_route_querydict_form_routed(valid_query):
    service = ImageProcessingService()

    result = service.route_querydict(QueryDict(valid_query["query"]))
    assert isinstance(result, valid_query["profile_form_class"])


def test_route_querydict_form_not_routed():
    service = ImageProcessingService()
    querydict = QueryDict(
        "profile_type=hogehoge&width=512&height=1024&color_rgb=B5F1CC&quality=63"
    )
    profile_types = ", ".join(
        [f'"{form_class.get_profile_type()}"' for form_class in service.form_classes]
    )
    error_message = f"このフィールドには次のうちいずれかの値を入力してください。({profile_types})"

    with pytest.raises(QueryError) as exc_info:
        service.route_querydict(querydict)
    assert exc_info.value.messages == {"profile_type": [error_message]}


def test_route_querydict_None():
    service = ImageProcessingService()
    querydict = QueryDict("width=512&height=1024&color_rgb=B5F1CC&quality=63")

    with pytest.raises(QueryError) as exc_info:
        service.route_querydict(querydict)

    error_message = "このフィールドは必須です"
    assert exc_info.value.messages == {"profile_type": [error_message]}


# ImageProcessingService.create_image()


def test_create_image_quality_None(temp_dir):
    service = ImageProcessingService()
    sample_profile = PNGPlainProfile(
        width=265, height=411, color_rgb=ColorRGB(160, 132, 220), alpha=198
    )
    result_image_path = service.create_image(sample_profile, temp_dir)
    assert os.path.isfile(result_image_path)
    assert os.path.splitext(result_image_path)[1] == ".png"


def test_create_image_quality_not_None(temp_dir):
    service = ImageProcessingService()
    sample_profile = JPEGPlainProfile(
        width=123, height=856, color_rgb=ColorRGB(93, 56, 145), quality=70
    )
    result_image_path = service.create_image(sample_profile, temp_dir)
    assert os.path.isfile(result_image_path)
    assert os.path.splitext(result_image_path)[1] == ".jpeg"


def test_create_image_base_dir_not_exist():
    service = ImageProcessingService()
    sample_profile = JPEGPlainProfile(
        width=123, height=856, color_rgb=ColorRGB(93, 56, 145), quality=70
    )
    fake_dir = "/path/to/fake/dir"
    expected_error_message = "No such directory. base_dir: /path/to/fake/dir"

    with pytest.raises(FileNotFoundError, match=expected_error_message):
        service.create_image(sample_profile, fake_dir)
