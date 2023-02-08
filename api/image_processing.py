from __future__ import annotations

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


# Exceptions
########################################################################################


class QueryError(Exception):
    def __init__(self, messages: dict[str, str | list[str]]):
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

    @classmethod
    @abstractmethod
    def get_extension(cls) -> str:
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
        self.width = width
        self.height = height
        self.color_rgb = color_rgb
        self._quality = quality

    def create_pil_image(self) -> PIL.Image.Image:
        pil_image = PIL.Image.new(
            "RGB", size=(self.width, self.height), color=self.color_rgb.to_tuple()
        )
        return pil_image

    @property
    def quality(self) -> int | None:
        return self._quality

    @classmethod
    def get_extension(cls) -> str:
        return "jpeg"


# Form fields
########################################################################################


hex_RGB_color_code_pattern = re.compile("[a-fA-F0-9]{3}|[a-fA-F0-9]{6}")


def validate_hex_RGB_color_code(value):
    match = hex_RGB_color_code_pattern.fullmatch(value)
    if match is None:
        raise ValidationError(f"{value} is not a valid hex RGB color code.")


def parse_hex_RGB_color_code(color_code_string):
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


class JPEGPlainProfileForm(ImageProfileForm):
    profile_class = JPEGPlainProfile

    width = forms.IntegerField(
        required=True,
        min_value=JPEGPlainProfile.min_size,
        max_value=JPEGPlainProfile.max_size,
    )
    height = forms.IntegerField(
        required=True,
        min_value=JPEGPlainProfile.min_size,
        max_value=JPEGPlainProfile.max_size,
    )
    color_rgb = HexRGBColorCodeField(
        required=True,
    )
    quality = forms.IntegerField(
        initial=75,
        min_value=JPEGPlainProfile.min_quality,
        max_value=JPEGPlainProfile.max_quality,
    )

    def get_profile(self) -> ImageProfileAbstract:
        if self.is_valid():
            return self.profile_class(**self.cleaned_data)
        else:
            raise QueryError(dict(self.errors))

    @classmethod
    def get_profile_type(cls) -> str:
        return "jpag_plain"
