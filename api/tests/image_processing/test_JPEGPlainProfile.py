import pytest

from api.image_processing import ColorRGB, JPEGPlainProfile, JPEGPlainProfileForm


@pytest.fixture(scope="session")
def profile_dict():
    return {
        "width": 512,
        "height": 1024,
        "color_rgb": ColorRGB(r=139, g=86, b=221),
        "quality": 65,
    }


def test_instantiate_from_dict(profile_dict):
    profile = JPEGPlainProfile(**profile_dict)
    assert profile.width == 512
    assert profile.height == 1024
    assert profile.color_rgb == ColorRGB(r=139, g=86, b=221)
    assert profile.quality == 65


def test_instantiate_without_arguments():
    profile = JPEGPlainProfile()
    assert profile.width == 48
    assert profile.height == 48
    assert profile.color_rgb == ColorRGB()
    assert profile.quality == 75


def test_numeric_field_clamp():
    profile_lt_min = JPEGPlainProfile(width=0, height=0, quality=-1)
    profile_gt_max = JPEGPlainProfile(width=15361, height=15361, quality=96)

    assert profile_lt_min.width == 1
    assert profile_lt_min.height == 1
    assert profile_lt_min.quality == 0

    assert profile_gt_max.width == 15360
    assert profile_gt_max.height == 15360
    assert profile_gt_max.quality == 95


def test_access_class_variables():
    assert JPEGPlainProfile.max_size == 15360
    assert JPEGPlainProfile.min_size == 1
    assert JPEGPlainProfile.max_quality == 95
    assert JPEGPlainProfile.min_quality == 0


def test_get_extension():
    assert JPEGPlainProfile.get_extension() == "jpeg"


def test_create_pil_image(profile_dict):
    profile = JPEGPlainProfile(**profile_dict)
    pil_image = profile.create_pil_image()
    assert pil_image.mode == "RGB"
    assert pil_image.width == 512
    assert pil_image.height == 1024


def test_upload_file_name(profile_dict):
    profile = JPEGPlainProfile(**profile_dict)
    assert (
        profile.upload_file_name
        == f"{JPEGPlainProfileForm.get_profile_type()}_width_512_height_1024_color_r_139_g_86_b_221_quality_65.{JPEGPlainProfile.get_extension()}"
    )


def test_dump_signiture(profile_dict):
    profile = JPEGPlainProfile(**profile_dict)
    assert profile.dump_signiture() == '{"%s":{"width":512,"height":1024,"color_rgb":{"r":139,"g":86,"b":221},"quality":65}}' % (
        JPEGPlainProfileForm.get_profile_type(),
    )
