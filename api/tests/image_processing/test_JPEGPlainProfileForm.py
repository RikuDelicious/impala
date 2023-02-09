import pytest
from django.http import QueryDict

from api.image_processing import (
    ColorRGB,
    JPEGPlainProfile,
    JPEGPlainProfileForm,
    QueryError,
)

# Fixtures
########################################################################################


@pytest.fixture
def querydict_all_proper():
    return QueryDict(
        "profile_type=jpeg_plain&width=512&height=256&color_rgb=85CDFD&quality=50"
    )


@pytest.fixture
def querydict_improper():
    return QueryDict("profile_type=jpeg_plain&width=512&height=256&quality=50")


# Tests
########################################################################################


def test_get_profile_type():
    assert JPEGPlainProfileForm.get_profile_type() == "jpeg_plain"
    assert JPEGPlainProfileForm().get_profile_type() == "jpeg_plain"


def test_querydict_all_proper_bind(querydict_all_proper):
    form = JPEGPlainProfileForm(querydict_all_proper)
    assert form.is_valid()
    assert form.cleaned_data == {
        "width": 512,
        "height": 256,
        "color_rgb": ColorRGB(r=133, g=205, b=253),
        "quality": 50,
    }


def test_querydict_all_proper_get_profile(querydict_all_proper):
    form = JPEGPlainProfileForm(querydict_all_proper)
    profile = form.get_profile()
    assert isinstance(profile, JPEGPlainProfile)
    assert profile.width == 512
    assert profile.height == 256
    assert profile.color_rgb == ColorRGB(r=133, g=205, b=253)
    assert profile.quality == 50


def test_querydict_improper_bind(querydict_improper):
    form = JPEGPlainProfileForm(querydict_improper)
    assert not form.is_valid()
    assert bool(form.errors)


def test_querydict_improper_get_profile(querydict_improper):
    form = JPEGPlainProfileForm(querydict_improper)
    with pytest.raises(QueryError):
        form.get_profile()
