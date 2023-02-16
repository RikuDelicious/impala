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


def test_required_field():
    form_without_width = JPEGPlainProfileForm(
        QueryDict("profile_type=jpeg_plain&height=256&color_rgb=85CDFD&quality=50")
    )
    form_without_height = JPEGPlainProfileForm(
        QueryDict("profile_type=jpeg_plain&width=512&color_rgb=85CDFD&quality=50")
    )
    form_without_color_rgb = JPEGPlainProfileForm(
        QueryDict("profile_type=jpeg_plain&width=512&height=256&quality=50")
    )
    form_without_quality = JPEGPlainProfileForm(
        QueryDict("profile_type=jpeg_plain&width=512&height=256&color_rgb=85CDFD")
    )

    assert not form_without_width.is_valid()
    assert form_without_width.errors == {"width": ["This field is required."]}
    assert not form_without_height.is_valid()
    assert form_without_height.errors == {"height": ["This field is required."]}
    assert not form_without_color_rgb.is_valid()
    assert form_without_color_rgb.errors == {"color_rgb": ["This field is required."]}
    assert not form_without_quality.is_valid()
    assert form_without_quality.errors == {"quality": ["This field is required."]}


def test_field_min_values():
    form = JPEGPlainProfileForm(
        QueryDict("profile_type=jpeg_plain&width=1&height=1&color_rgb=000000&quality=0")
    )
    assert form.is_valid()


def test_field_lt_min_values():
    form_lt_min_width = JPEGPlainProfileForm(
        QueryDict(
            "profile_type=jpeg_plain&width=0&height=256&color_rgb=85CDFD&quality=50"
        )
    )
    form_lt_min_height = JPEGPlainProfileForm(
        QueryDict(
            "profile_type=jpeg_plain&width=512&height=0&color_rgb=85CDFD&quality=50"
        )
    )
    form_lt_min_quality = JPEGPlainProfileForm(
        QueryDict(
            "profile_type=jpeg_plain&width=512&height=256&color_rgb=85CDFD&quality=-1"
        )
    )

    assert not form_lt_min_width.is_valid()
    assert form_lt_min_width.errors == {
        "width": ["Ensure this value is greater than or equal to 1."]
    }
    assert not form_lt_min_height.is_valid()
    assert form_lt_min_height.errors == {
        "height": ["Ensure this value is greater than or equal to 1."]
    }
    assert not form_lt_min_quality.is_valid()
    assert form_lt_min_quality.errors == {
        "quality": ["Ensure this value is greater than or equal to 0."]
    }


def test_field_max_values():
    form = JPEGPlainProfileForm(
        QueryDict(
            "profile_type=jpeg_plain&width=15360&height=15360&color_rgb=FFFFFF&quality=95"
        )
    )
    assert form.is_valid()


def test_field_gt_max_values():
    form_gt_max_width = JPEGPlainProfileForm(
        QueryDict(
            "profile_type=jpeg_plain&width=15361&height=256&color_rgb=85CDFD&quality=50"
        )
    )
    form_gt_max_height = JPEGPlainProfileForm(
        QueryDict(
            "profile_type=jpeg_plain&width=512&height=15361&color_rgb=85CDFD&quality=50"
        )
    )
    form_gt_max_quality = JPEGPlainProfileForm(
        QueryDict(
            "profile_type=jpeg_plain&width=512&height=256&color_rgb=85CDFD&quality=96"
        )
    )

    assert not form_gt_max_width.is_valid()
    assert form_gt_max_width.errors == {
        "width": ["Ensure this value is less than or equal to 15360."]
    }
    assert not form_gt_max_height.is_valid()
    assert form_gt_max_height.errors == {
        "height": ["Ensure this value is less than or equal to 15360."]
    }
    assert not form_gt_max_quality.is_valid()
    assert form_gt_max_quality.errors == {
        "quality": ["Ensure this value is less than or equal to 95."]
    }


def test_field_improper_values():
    form_improper_width = JPEGPlainProfileForm(
        QueryDict(
            "profile_type=jpeg_plain&width=hoge&height=256&color_rgb=85CDFD&quality=50"
        )
    )
    form_improper_height = JPEGPlainProfileForm(
        QueryDict(
            "profile_type=jpeg_plain&width=512&height=hoge&color_rgb=85CDFD&quality=50"
        )
    )
    form_improper_color_rgb = JPEGPlainProfileForm(
        QueryDict(
            "profile_type=jpeg_plain&width=512&height=256&color_rgb=85CD&quality=50"
        )
    )
    form_improper_quality = JPEGPlainProfileForm(
        QueryDict(
            "profile_type=jpeg_plain&width=512&height=256&color_rgb=85CDFD&quality=hoge"
        )
    )

    assert not form_improper_width.is_valid()
    assert form_improper_width.errors == {"width": ["Enter a whole number."]}
    assert not form_improper_height.is_valid()
    assert form_improper_height.errors == {"height": ["Enter a whole number."]}
    assert not form_improper_color_rgb.is_valid()
    assert form_improper_color_rgb.errors == {
        "color_rgb": ["85CD is not a valid hex RGB color code."]
    }
    assert not form_improper_quality.is_valid()
    assert form_improper_quality.errors == {"quality": ["Enter a whole number."]}


def test_get_query_string_valid(querydict_all_proper):
    form = JPEGPlainProfileForm(querydict_all_proper)
    assert (
        form.get_query_string()
        == "profile_type=jpeg_plain&width=512&height=256&color_rgb=85CDFD&quality=50"
    )


def test_get_query_string_invalid(querydict_improper):
    form = JPEGPlainProfileForm(querydict_improper)
    with pytest.raises(QueryError):
        form.get_query_string()
