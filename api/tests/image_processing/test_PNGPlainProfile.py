import pytest

from api.image_processing import ColorRGB, PNGPlainProfile


@pytest.fixture(scope="session")
def profile_dict():
    return {
        "width": 512,
        "height": 1024,
        "color_rgb": ColorRGB(r=139, g=86, b=221),
        "alpha": 193,
    }


def test_instantiate_from_dict(profile_dict):
    profile = PNGPlainProfile(**profile_dict)
    assert profile.width == 512
    assert profile.height == 1024
    assert profile.color_rgb == ColorRGB(r=139, g=86, b=221)
    assert profile.alpha == 193


def test_instantiate_without_arguments():
    profile = PNGPlainProfile()
    assert profile.width == 48
    assert profile.height == 48
    assert profile.color_rgb == ColorRGB()
    assert profile.alpha == 255


def test_numeric_field_clamp():
    profile_lt_min = PNGPlainProfile(width=0, height=0, alpha=-1)
    profile_gt_max = PNGPlainProfile(width=15361, height=15361, alpha=256)

    assert profile_lt_min.width == 1
    assert profile_lt_min.height == 1
    assert profile_lt_min.alpha == 0

    assert profile_gt_max.width == 15360
    assert profile_gt_max.height == 15360
    assert profile_gt_max.alpha == 255


def test_access_class_variables():
    assert PNGPlainProfile.max_size == 15360
    assert PNGPlainProfile.min_size == 1
    assert PNGPlainProfile.max_alpha == 255
    assert PNGPlainProfile.min_alpha == 0


def test_get_extension():
    assert PNGPlainProfile.get_extension() == "png"


def test_create_pil_image(profile_dict):
    profile = PNGPlainProfile(**profile_dict)
    pil_image = profile.create_pil_image()
    assert pil_image.mode == "RGBA"
    assert pil_image.width == 512
    assert pil_image.height == 1024
