from __future__ import annotations

from django import forms


class QueryError(Exception):
    def __init__(self, messages: dict[str, str]):
        self.messages = messages


class ImageProfileAbstract:
    pass


class ImageProfileForm(forms.Form):
    def get_profile(self) -> ImageProfileAbstract:
        raise NotImplementedError()
