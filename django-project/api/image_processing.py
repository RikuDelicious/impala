from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod
from collections import OrderedDict
from dataclasses import dataclass

import PIL.Image
from django import forms
from django.core.exceptions import ValidationError

# Helper functions
########################################################################################


def clamp(value: int, min: int, max: int):
    if min > max:
        raise ValueError("argument min is bigger than max.")
    if value < min:
        return min
    if value > max:
        return max
    return value


def jsondump_fixed(ordered_dict: OrderedDict) -> str:
    return json.dumps(
        ordered_dict,
        separators=(",", ":"),
        indent=None,
        sort_keys=False,
        ensure_ascii=True,
    )


# Exceptions
########################################################################################


class QueryError(Exception):
    def __init__(self, messages: dict[str, str] | dict[str, list[str]]):
        self.messages = messages


# dataclasses
########################################################################################


@dataclass(init=False, frozen=True)
class ColorRGB:
    r: int = 0
    g: int = 0
    b: int = 0

    max_value = 255
    min_value = 0

    def __init__(self, r: int = 0, g: int = 0, b: int = 0):
        object.__setattr__(self, "r", clamp(r, self.min_value, self.max_value))
        object.__setattr__(self, "g", clamp(g, self.min_value, self.max_value))
        object.__setattr__(self, "b", clamp(b, self.min_value, self.max_value))

    def to_tuple(self) -> tuple:
        return (self.r, self.g, self.b)

    def to_ordered_dict(self) -> OrderedDict:
        return OrderedDict(r=self.r, g=self.g, b=self.b)


# Image Profiles
########################################################################################


class ImageProfileAbstract(ABC):
    @abstractmethod
    def create_pil_image(self) -> PIL.Image.Image:
        raise NotImplementedError()

    @property
    @abstractmethod
    def quality(self) -> int | None:
        raise NotImplementedError()

    @property
    @abstractmethod
    def upload_file_name(self) -> str:
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def get_extension(cls) -> str:
        raise NotImplementedError()

    @abstractmethod
    def dump_signiture(self) -> str:
        raise NotImplementedError()


class JPEGPlainProfile(ImageProfileAbstract):
    max_size: int = 15360
    min_size: int = 1
    max_quality: int = 95
    min_quality: int = 0

    def __init__(
        self,
        width: int = 48,
        height: int = 48,
        color_rgb: ColorRGB = ColorRGB(),
        quality: int = 75,
    ):
        self.width = clamp(width, self.min_size, self.max_size)
        self.height = clamp(height, self.min_size, self.max_size)
        self.color_rgb = color_rgb
        self._quality = clamp(quality, self.min_quality, self.max_quality)

    def create_pil_image(self) -> PIL.Image.Image:
        pil_image = PIL.Image.new(
            "RGB", size=(self.width, self.height), color=self.color_rgb.to_tuple()
        )
        return pil_image

    @property
    def quality(self) -> int | None:
        return self._quality

    @property
    def upload_file_name(self) -> str:
        return f"jpeg_plain_width_{self.width}_height_{self.height}_color_r_{self.color_rgb.r}_g_{self.color_rgb.g}_b_{self.color_rgb.b}_quality_{self.quality}.{self.get_extension()}"

    @classmethod
    def get_extension(cls) -> str:
        return "jpeg"

    def dump_signiture(self) -> str:
        signiture_dict = OrderedDict(
            jpeg_plain=OrderedDict(
                width=self.width,
                height=self.height,
                color_rgb=self.color_rgb.to_ordered_dict(),
                quality=self.quality,
            ),
        )
        return jsondump_fixed(signiture_dict)


class PNGPlainProfile(ImageProfileAbstract):
    max_size: int = 15360
    min_size: int = 1
    max_alpha = 255
    min_alpha = 0

    def __init__(
        self,
        width: int = 48,
        height: int = 48,
        color_rgb: ColorRGB = ColorRGB(),
        alpha: int = 255,
    ):
        self.width = clamp(width, self.min_size, self.max_size)
        self.height = clamp(height, self.min_size, self.max_size)
        self.color_rgb = color_rgb
        self.alpha = clamp(alpha, self.min_alpha, self.max_alpha)

    def create_pil_image(self) -> PIL.Image.Image:
        pil_image = PIL.Image.new(
            mode="RGB",
            size=(self.width, self.height),
            color=self.color_rgb.to_tuple(),
        )
        pil_image.putalpha(self.alpha)
        return pil_image

    @property
    def quality(self) -> int | None:
        return None

    @property
    def upload_file_name(self) -> str:
        return f"png_plain_width_{self.width}_height_{self.height}_color_r_{self.color_rgb.r}_g_{self.color_rgb.g}_b_{self.color_rgb.b}_alpha_{self.alpha}.{self.get_extension()}"

    @classmethod
    def get_extension(cls) -> str:
        return "png"

    def dump_signiture(self) -> str:
        signiture_dict = OrderedDict(
            png_plain=OrderedDict(
                width=self.width,
                height=self.height,
                color_rgb=self.color_rgb.to_ordered_dict(),
                alpha=self.alpha,
            )
        )
        return jsondump_fixed(signiture_dict)


# Form fields
########################################################################################


hex_RGB_color_code_pattern = re.compile("[a-fA-F0-9]{3}|[a-fA-F0-9]{6}")


def validate_hex_RGB_color_code(value):
    match = hex_RGB_color_code_pattern.fullmatch(value)
    if match is None:
        raise ValidationError(f"{value} is not a valid hex RGB color code.")


def parse_hex_RGB_color_code(color_code_string):
    """
    カラーコード文字列を数値に変換する
    既に検証を通過した文字列が渡される想定のため、
    この関数では再度バリデーションは行わない
    """
    if len(color_code_string) == 3:
        hex_srtings = [s + s for s in color_code_string]
    elif len(color_code_string) == 6:
        hex_srtings = [color_code_string[2 * i : 2 * (i + 1)] for i in range(3)]
    numeric_values = [int(value, 16) for value in hex_srtings]
    return tuple(numeric_values)


class HexRGBColorCodeField(forms.CharField):
    default_validators = [validate_hex_RGB_color_code]

    def clean(self, value):
        cleaned_data = super().clean(value)
        self.original_cleaned_data = cleaned_data
        rgb_tuple = parse_hex_RGB_color_code(cleaned_data)
        return ColorRGB(r=rgb_tuple[0], g=rgb_tuple[1], b=rgb_tuple[2])


# Image Profile Forms
########################################################################################


class ImageProfileForm(forms.Form):
    def get_profile(self) -> ImageProfileAbstract:
        raise NotImplementedError()

    @classmethod
    def get_profile_type(cls) -> str:
        raise NotImplementedError()

    def get_query_string(self) -> str:
        raise NotImplementedError()

    @classmethod
    def get_description(cls) -> str:
        raise NotImplementedError()


class JPEGPlainProfileForm(ImageProfileForm):
    profile_class = JPEGPlainProfile

    width = forms.IntegerField(
        required=True,
        initial=512,
        min_value=JPEGPlainProfile.min_size,
        max_value=JPEGPlainProfile.max_size,
        help_text=f"画像の横サイズ（{JPEGPlainProfile.min_size} ~ {JPEGPlainProfile.max_size} px）",
    )
    height = forms.IntegerField(
        required=True,
        initial=512,
        min_value=JPEGPlainProfile.min_size,
        max_value=JPEGPlainProfile.max_size,
        help_text=f"画像の縦サイズ（{JPEGPlainProfile.min_size} ~ {JPEGPlainProfile.max_size} px）",
    )
    color_rgb = HexRGBColorCodeField(
        required=True, initial="000000", help_text="6桁または3桁のカラーコード（例：537FE7, fff）"
    )
    quality = forms.IntegerField(
        required=True,
        initial=75,
        min_value=JPEGPlainProfile.min_quality,
        max_value=JPEGPlainProfile.max_quality,
        help_text=f"画像のクオリティ（{JPEGPlainProfile.min_quality} ~ {JPEGPlainProfile.max_quality}）",
    )

    def get_profile(self) -> ImageProfileAbstract:
        if self.is_valid():
            return self.profile_class(**self.cleaned_data)
        else:
            raise QueryError(dict(self.errors))

    @classmethod
    def get_profile_type(cls) -> str:
        return "jpeg_plain"

    def get_query_string(self) -> str:
        if self.is_valid():
            cleaned_data = self.cleaned_data.copy()
            cleaned_data["color_rgb"] = self.fields["color_rgb"].original_cleaned_data

            parameters = [f"profile_type={self.get_profile_type()}"] + [
                f"{key}={value}" for key, value in cleaned_data.items()
            ]
            query_string = "&".join(parameters)
            return query_string
        else:
            raise QueryError(dict(self.errors))

    @classmethod
    def get_description(cls) -> str:
        return "JPEG形式の無地カラー画像"


class PNGPlainProfileForm(ImageProfileForm):
    profile_class = PNGPlainProfile

    width = forms.IntegerField(
        required=True,
        initial=512,
        min_value=PNGPlainProfile.min_size,
        max_value=PNGPlainProfile.max_size,
        help_text=f"画像の横サイズ（{PNGPlainProfile.min_size} ~ {PNGPlainProfile.max_size} px）",
    )
    height = forms.IntegerField(
        required=True,
        initial=512,
        min_value=PNGPlainProfile.min_size,
        max_value=PNGPlainProfile.max_size,
        help_text=f"画像の縦サイズ（{PNGPlainProfile.min_size} ~ {PNGPlainProfile.max_size} px）",
    )
    color_rgb = HexRGBColorCodeField(
        required=True, initial="000000", help_text="6桁または3桁のカラーコード（例：537FE7, fff）"
    )
    alpha = forms.IntegerField(
        required=True,
        initial=255,
        min_value=PNGPlainProfile.min_alpha,
        max_value=PNGPlainProfile.max_alpha,
        help_text=f"画像のアルファ値（{PNGPlainProfile.min_alpha} ~ {PNGPlainProfile.max_alpha}）",
    )

    def get_profile(self) -> ImageProfileAbstract:
        if self.is_valid():
            return self.profile_class(**self.cleaned_data)
        else:
            raise QueryError(dict(self.errors))

    @classmethod
    def get_profile_type(cls) -> str:
        return "png_plain"

    def get_query_string(self) -> str:
        if self.is_valid():
            cleaned_data = self.cleaned_data.copy()
            cleaned_data["color_rgb"] = self.fields["color_rgb"].original_cleaned_data

            parameters = [f"profile_type={self.get_profile_type()}"] + [
                f"{key}={value}" for key, value in cleaned_data.items()
            ]
            query_string = "&".join(parameters)
            return query_string
        else:
            raise QueryError(dict(self.errors))

    @classmethod
    def get_description(cls) -> str:
        return "PNG形式の無地カラー画像"
