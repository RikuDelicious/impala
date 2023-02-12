from __future__ import annotations

import os
from abc import ABC, abstractmethod
from typing import Type

from django.core.files import File
from django.http import QueryDict

from . import models
from .image_processing import (
    ImageProfileAbstract,
    ImageProfileForm,
    JPEGPlainProfileForm,
    PNGPlainProfileForm,
    QueryError,
)


class ImageProcessingServiceAbstract(ABC):
    @classmethod
    @abstractmethod
    def create_profile(cls, querydict: QueryDict) -> ImageProfileAbstract:
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def create_image(cls, profile: ImageProfileAbstract, base_dir: str) -> str:
        raise NotImplementedError()


class ImageProcessingService(ImageProcessingServiceAbstract):
    form_classes: list[Type[ImageProfileForm]] = [
        JPEGPlainProfileForm,
        PNGPlainProfileForm,
    ]

    @classmethod
    def route_querydict(cls, querydict: QueryDict) -> ImageProfileForm:
        """
        引数querydictを解析できない場合、QueryError例外が発生する
        """
        profile_type = querydict.get("profile_type", None)

        for form_class in cls.form_classes:
            if profile_type == form_class.get_profile_type():
                form = form_class(querydict)
                return form

        if profile_type is None:
            error_message = "このフィールドは必須です"
        else:
            expected_values = ", ".join(
                [
                    f'"{form_class.get_profile_type()}"'
                    for form_class in cls.form_classes
                ]
            )
            error_message = f"このフィールドには次のうちいずれかの値を入力してください。({expected_values})"

        raise QueryError({"profile_type": [error_message]})

    @classmethod
    def create_profile(cls, querydict: QueryDict) -> ImageProfileAbstract:
        profile_form = cls.route_querydict(querydict)
        if profile_form.is_valid():
            return profile_form.get_profile()
        else:
            raise QueryError(dict(profile_form.errors))

    @classmethod
    def create_image(cls, profile: ImageProfileAbstract, base_dir: str) -> str:
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
    @classmethod
    @abstractmethod
    def get_cache_image_url(cls, profile: ImageProfileAbstract) -> str | None:
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def upload_image(cls, image_path: str, profile: ImageProfileAbstract) -> str:
        raise NotImplementedError()


class ImageModelService:
    model = models.Image

    @classmethod
    def get_cache_image_url(cls, profile: ImageProfileAbstract) -> str | None:
        queryset = cls.model.objects.filter(profile_signiture=profile.dump_signiture())
        if queryset.exists():
            return queryset.first()
        else:
            return None

    @classmethod
    def upload_image(cls, image_path: str, profile: ImageProfileAbstract) -> str:
        with open(image_path, "rb") as f:
            upload_file = File(f, name=profile.upload_file_name)
            image = cls.model.objects.create(
                upload=upload_file, profile_signiture=profile.dump_signiture()
            )
            return image.upload.url
