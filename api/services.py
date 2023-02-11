from __future__ import annotations

import os
from abc import ABC, abstractmethod
from typing import Sequence, Type

from django.http import QueryDict

from .image_processing import (
    ImageProfileAbstract,
    ImageProfileForm,
    JPEGPlainProfileForm,
    QueryError,
)


class ImageProcessingServiceAbstract(ABC):
    @abstractmethod
    def create_profile(self, querydict: QueryDict) -> ImageProfileAbstract:
        raise NotImplementedError()

    @abstractmethod
    def create_image(self, profile: ImageProfileAbstract, base_dir: str) -> str:
        raise NotImplementedError()


class ImageProcessingService(ImageProcessingServiceAbstract):
    form_classes: list[Type[ImageProfileForm]] = [JPEGPlainProfileForm]

    def route_querydict(self, querydict: QueryDict) -> ImageProfileForm:
        """
        引数querydictを解析できない場合、QueryError例外が発生する
        """
        profile_type = querydict.get("profile_type", None)

        for form_class in self.form_classes:
            if profile_type == form_class.get_profile_type():
                form = form_class(querydict)
                return form

        if profile_type is None:
            error_message = "このフィールドは必須です"
        else:
            expected_values = ", ".join(
                [
                    f'"{form_class.get_profile_type()}"'
                    for form_class in self.form_classes
                ]
            )
            error_message = f"このフィールドには次のうちいずれかの値を入力してください。({expected_values})"

        raise QueryError({"profile_type": [error_message]})

    def create_profile(self, querydict: QueryDict) -> ImageProfileAbstract:
        profile_form = self.route_querydict(querydict)
        if profile_form.is_valid():
            return profile_form.get_profile()
        else:
            raise QueryError(dict(profile_form.errors))

    def create_image(self, profile: ImageProfileAbstract, base_dir: str) -> str:
        pil_image = profile.create_pil_image()
        if os.path.isdir(base_dir):
            tmp_image_path = os.path.join(base_dir, f"tmp.{profile.get_extension()}")
        else:
            raise FileNotFoundError(f"No such directory. base_dir: {base_dir}")

        if profile.quality is None:
            pil_image.save(tmp_image_path)
        else:
            pil_image.save(tmp_image_path, quality=profile.quality)

        return tmp_image_path


class ImageModelServiceAbstract(ABC):
    @abstractmethod
    def get_cache_image_url(self, profile: ImageProfileAbstract) -> str | None:
        raise NotImplementedError()

    @abstractmethod
    def upload_image(self, image_path: str) -> str:
        raise NotImplementedError()


class ImageModelService:
    def get_cache_image_url(self, profile: ImageProfileAbstract) -> str | None:
        raise NotImplementedError()

    def upload_image(self, image_path: str) -> str:
        raise NotImplementedError()
