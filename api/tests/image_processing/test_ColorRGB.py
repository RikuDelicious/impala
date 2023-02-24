from collections import OrderedDict

from api.image_processing import ColorRGB


def test_instantiate():
    color_rgb = ColorRGB(5, 240, 193)
    assert color_rgb.r == 5
    assert color_rgb.g == 240
    assert color_rgb.b == 193


def test_instantiate_without_arguments():
    color_rgb = ColorRGB()
    assert color_rgb.r == 0
    assert color_rgb.g == 0
    assert color_rgb.b == 0


def test_instantiate_with_keyword_arguments():
    color_rgb = ColorRGB(r=219, g=4, b=233)
    assert color_rgb.r == 219
    assert color_rgb.g == 4
    assert color_rgb.b == 233


def test_clamp():
    color_lt_min = ColorRGB(-1, -1, -1)
    color_gt_max = ColorRGB(256, 256, 256)

    assert color_lt_min.r == 0
    assert color_lt_min.g == 0
    assert color_lt_min.b == 0
    assert color_gt_max.r == 255
    assert color_gt_max.g == 255
    assert color_gt_max.b == 255


def test_to_tuple():
    color_rgb = ColorRGB(r=219, g=4, b=233)
    assert color_rgb.to_tuple() == (219, 4, 233)


def test_to_ordered_dict():
    color_rgb = ColorRGB(r=219, g=4, b=233)
    assert color_rgb.to_ordered_dict() == OrderedDict(r=219, g=4, b=233)
