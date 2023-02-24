import pytest
from django.http import QueryDict

from api.image_processing import (
    ColorRGB,
    PNGPlainProfile,
    PNGPlainProfileForm,
    QueryError,
)

# Fixtures
########################################################################################


@pytest.fixture
def querydict_all_proper():
    return QueryDict(
        "profile_type=png_plain&width=512&height=256&color_rgb=85CDFD&alpha=193"
    )


@pytest.fixture
def querydict_improper():
    return QueryDict("profile_type=png_plain&width=512&height=256&quality=50")


# Tests
########################################################################################


def test_get_profile_type():
    assert PNGPlainProfileForm.get_profile_type() == "png_plain"
    assert PNGPlainProfileForm().get_profile_type() == "png_plain"


def test_querydict_all_proper_bind(querydict_all_proper):
    form = PNGPlainProfileForm(querydict_all_proper)
    assert form.is_valid()
    assert form.cleaned_data == {
        "width": 512,
        "height": 256,
        "color_rgb": ColorRGB(r=133, g=205, b=253),
        "alpha": 193,
    }


def test_querydict_all_proper_get_profile(querydict_all_proper):
    form = PNGPlainProfileForm(querydict_all_proper)
    profile = form.get_profile()
    assert isinstance(profile, PNGPlainProfile)
    assert profile.width == 512
    assert profile.height == 256
    assert profile.color_rgb == ColorRGB(r=133, g=205, b=253)
    assert profile.alpha == 193


def test_querydict_improper_bind(querydict_improper):
    form = PNGPlainProfileForm(querydict_improper)
    assert not form.is_valid()
    assert bool(form.errors)


def test_querydict_improper_get_profile(querydict_improper):
    form = PNGPlainProfileForm(querydict_improper)
    with pytest.raises(QueryError):
        form.get_profile()


def test_required_field():
    form_without_width = PNGPlainProfileForm(
        QueryDict("profile_type=png_plain&height=256&color_rgb=85CDFD&alpha=193")
    )
    form_without_height = PNGPlainProfileForm(
        QueryDict("profile_type=png_plain&width=512&color_rgb=85CDFD&alpha=193")
    )
    form_without_color_rgb = PNGPlainProfileForm(
        QueryDict("profile_type=png_plain&width=512&height=256&alpha=193")
    )
    form_without_alpha = PNGPlainProfileForm(
        QueryDict("profile_type=png_plain&width=512&height=256&color_rgb=85CDFD")
    )

    assert not form_without_width.is_valid()
    assert form_without_width.errors == {"width": ["This field is required."]}
    assert not form_without_height.is_valid()
    assert form_without_height.errors == {"height": ["This field is required."]}
    assert not form_without_color_rgb.is_valid()
    assert form_without_color_rgb.errors == {"color_rgb": ["This field is required."]}
    assert not form_without_alpha.is_valid()
    assert form_without_alpha.errors == {"alpha": ["This field is required."]}


def test_field_min_values():
    form = PNGPlainProfileForm(
        QueryDict("profile_type=png_plain&width=1&height=1&color_rgb=000000&alpha=0")
    )
    assert form.is_valid()


def test_field_lt_min_values():
    form_lt_min_width = PNGPlainProfileForm(
        QueryDict(
            "profile_type=png_plain&width=0&height=256&color_rgb=85CDFD&alpha=193"
        )
    )
    form_lt_min_height = PNGPlainProfileForm(
        QueryDict(
            "profile_type=png_plain&width=512&height=0&color_rgb=85CDFD&alpha=193"
        )
    )
    form_lt_min_alpha = PNGPlainProfileForm(
        QueryDict(
            "profile_type=png_plain&width=512&height=256&color_rgb=85CDFD&alpha=-1"
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
    assert not form_lt_min_alpha.is_valid()
    assert form_lt_min_alpha.errors == {
        "alpha": ["Ensure this value is greater than or equal to 0."]
    }


def test_field_max_values():
    form = PNGPlainProfileForm(
        QueryDict(
            "profile_type=png_plain&width=15360&height=15360&color_rgb=FFFFFF&alpha=255"
        )
    )
    assert form.is_valid()


def test_field_gt_max_values():
    form_gt_max_width = PNGPlainProfileForm(
        QueryDict(
            "profile_type=png_plain&width=15361&height=256&color_rgb=85CDFD&alpha=193"
        )
    )
    form_gt_max_height = PNGPlainProfileForm(
        QueryDict(
            "profile_type=png_plain&width=512&height=15361&color_rgb=85CDFD&alpha=193"
        )
    )
    form_gt_max_alpha = PNGPlainProfileForm(
        QueryDict(
            "profile_type=png_plain&width=512&height=256&color_rgb=85CDFD&alpha=256"
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
    assert not form_gt_max_alpha.is_valid()
    assert form_gt_max_alpha.errors == {
        "alpha": ["Ensure this value is less than or equal to 255."]
    }


def test_field_improper_values():
    form_improper_width = PNGPlainProfileForm(
        QueryDict(
            "profile_type=png_plain&width=hoge&height=256&color_rgb=85CDFD&alpha=193"
        )
    )
    form_improper_height = PNGPlainProfileForm(
        QueryDict(
            "profile_type=png_plain&width=512&height=hoge&color_rgb=85CDFD&alpha=193"
        )
    )
    form_improper_color_rgb = PNGPlainProfileForm(
        QueryDict(
            "profile_type=png_plain&width=512&height=256&color_rgb=85CD&alpha=193"
        )
    )
    form_improper_alpha = PNGPlainProfileForm(
        QueryDict(
            "profile_type=png_plain&width=512&height=256&color_rgb=85CDFD&alpha=hoge"
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
    assert not form_improper_alpha.is_valid()
    assert form_improper_alpha.errors == {"alpha": ["Enter a whole number."]}


def test_get_query_string_valid(querydict_all_proper):
    form = PNGPlainProfileForm(querydict_all_proper)
    assert (
        form.get_query_string()
        == "profile_type=png_plain&width=512&height=256&color_rgb=85CDFD&alpha=193"
    )


def test_get_query_string_invalid(querydict_improper):
    form = PNGPlainProfileForm(querydict_improper)
    with pytest.raises(QueryError):
        form.get_query_string()
