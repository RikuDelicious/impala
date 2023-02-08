from __future__ import annotations

from abc import ABC, abstractmethod

from django import forms
from PIL.Image import Image

# Exceptions
########################################################################################


class QueryError(Exception):
    def __init__(self, messages: dict[str, str | list[str]]):
        self.messages = messages


# Image Profiles
########################################################################################


class ImageProfileAbstract(ABC):
    @abstractmethod
    def create_pil_image(self) -> Image:
        raise NotImplementedError()

    @property
    @abstractmethod
    def quality(self) -> int | None:
        raise NotImplementedError()

    @quality.setter
    @abstractmethod
    def quality(self, value: int):
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def get_extension(cls) -> str:
        raise NotImplementedError()


# Image Profile Forms
########################################################################################


class ImageProfileForm(forms.Form):
    def get_profile(self) -> ImageProfileAbstract:
        raise NotImplementedError()

    @classmethod
    def get_profile_type(cls) -> str:
        raise NotImplementedError()
