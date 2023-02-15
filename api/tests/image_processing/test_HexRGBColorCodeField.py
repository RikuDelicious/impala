import pytest
from django.core.exceptions import ValidationError

from api.image_processing import (
    ColorRGB,
    HexRGBColorCodeField,
    hex_RGB_color_code_pattern,
    parse_hex_RGB_color_code,
    validate_hex_RGB_color_code,
)

# Plugins
########################################################################################


def valid_color_codes():
    """
    3桁・6桁の正しい形式のカラーコードをリストで返す。
    全てのパターンを返すわけではなく、各桁がa-fA-F0-9となるような
    最低限のカラーコードのみを返す。
    """
    characters_to_iterate = "123456789abcdefABCDEF"

    shorthand_codes = []
    for i in range(3):
        for c in characters_to_iterate:
            code = "000"
            code = code[:i] + c + code[i + 1 :]
            shorthand_codes.append(code)

    full_codes = []
    for i in range(6):
        for c in characters_to_iterate:
            code = "000000"
            code = code[:i] + c + code[i + 1 :]
            full_codes.append(code)

    return shorthand_codes + full_codes


def invalid_color_codes():
    """
    3桁及び6桁のカラーコードにマッチしないパターンの文字列をリストで返す
    以下の文字列を検証用の文字列として用意する。
    - 1桁、2桁、4桁、5桁、7桁の0-9a-fA-Fで構成される文字列
    - 3桁及び6桁の文字列で、0-9a-fA-F以外の文字が入っているもの
    """
    return ["0", "00", "0000", "00000", "0000000", "00z", "00000z"]


def pytest_generate_tests(metafunc):
    if "valid_color_code" in metafunc.fixturenames:
        metafunc.parametrize("valid_color_code", valid_color_codes())

    if "invalid_color_code" in metafunc.fixturenames:
        metafunc.parametrize("invalid_color_code", invalid_color_codes())


# Tests
########################################################################################

# hex_RGB_color_code_pattern


def test_hex_RGB_color_code_pattern_match(valid_color_code):
    """
    3桁及び6桁のカラーコードで、各桁でa-fA-F0-9の全ての文字が使えることを検証する

    （例）3桁のカラーコードの第一桁の文字がa-fA-F0-9となる以下のカラーコードを用意する
        -> 000, 100, 200, ... , a00, b00, c00, ... , A00, B00, C00, ... , F00
        第二桁以降でも上記と同様のパターンのカラーコードを用意して検証する
    """
    assert hex_RGB_color_code_pattern.fullmatch(valid_color_code) is not None


def test_hex_RGB_color_code_pattern_not_match(invalid_color_code):
    assert hex_RGB_color_code_pattern.fullmatch(invalid_color_code) is None


# validate_hex_RGB_color_code


def test_validate_hex_RGB_color_code_valid(valid_color_code):
    try:
        validate_hex_RGB_color_code(valid_color_code)
    except Exception as ex:
        pytest.fail(ex)


def test_validate_hex_RGB_color_code_invalid(invalid_color_code):
    with pytest.raises(
        ValidationError,
        match=f"{invalid_color_code} is not a valid hex RGB color code.",
    ):
        validate_hex_RGB_color_code(invalid_color_code)


# parse_hex_RGB_color_code


@pytest.mark.parametrize(
    "code, rgb_values",
    [
        ("000", (0, 0, 0)),
        ("678", (102, 119, 136)),
        ("abc", (170, 187, 204)),
        ("fff", (255, 255, 255)),
    ],
)
def test_parse_hex_RGB_color_code_shorthand(code, rgb_values):
    assert parse_hex_RGB_color_code(code) == rgb_values


@pytest.mark.parametrize(
    "code, rgb_values",
    [
        ("000000", (0, 0, 0)),
        ("324C96", (50, 76, 150)),
        ("C67345", (198, 115, 69)),
        ("FFFFFF", (255, 255, 255)),
    ],
)
def test_parse_hex_RGB_color_code_full(code, rgb_values):
    assert parse_hex_RGB_color_code(code) == rgb_values


# HexRGBColorCodeField


@pytest.mark.parametrize(
    "code, color_rgb",
    [
        ("000", ColorRGB(0, 0, 0)),
        ("678", ColorRGB(102, 119, 136)),
        ("abc", ColorRGB(170, 187, 204)),
        ("fff", ColorRGB(255, 255, 255)),
    ],
)
def test_HexRGBColorCodeField_clean_valid_shorthand(code, color_rgb):
    field = HexRGBColorCodeField()
    result = field.clean(code)
    assert result == color_rgb


@pytest.mark.parametrize(
    "code, color_rgb",
    [
        ("000000", ColorRGB(0, 0, 0)),
        ("324C96", ColorRGB(50, 76, 150)),
        ("C67345", ColorRGB(198, 115, 69)),
        ("FFFFFF", ColorRGB(255, 255, 255)),
    ],
)
def test_HexRGBColorCodeField_clean_valid_full(code, color_rgb):
    field = HexRGBColorCodeField()
    result = field.clean(code)
    assert result == color_rgb


def test_HexRGBColorCodeField_clean_invalid(invalid_color_code):
    field = HexRGBColorCodeField()
    with pytest.raises(
        ValidationError,
        match=f"{invalid_color_code} is not a valid hex RGB color code.",
    ):
        field.clean(invalid_color_code)
