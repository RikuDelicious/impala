import pytest
from django.core.exceptions import ValidationError

from api.image_processing import hex_RGB_color_code_pattern, validate_hex_RGB_color_code


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