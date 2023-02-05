from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from django.http import QueryDict

from .image_processing import ImageProfileAbstract, ImageProfileForm, QueryError


class ImageProcessingServiceAbstract(ABC):
    @abstractmethod
    def create_profile(self, querydict: QueryDict) -> ImageProfileAbstract:
        raise NotImplementedError()

    @abstractmethod
    def create_image(self, profile: ImageProfileAbstract) -> Path:
        raise NotImplementedError()


class ImageProcessingService(ImageProcessingServiceAbstract):
    def route_querydict(self, querydict: QueryDict) -> ImageProfileForm:
        raise NotImplementedError()

    def create_profile(self, querydict: QueryDict) -> ImageProfileAbstract:
        profile_form = self.route_querydict(querydict)
        if profile_form.is_valid():
            return profile_form.get_profile()
        else:
            raise QueryError(dict(profile_form.errors))

    def create_image(self, profile: ImageProfileAbstract) -> Path:
        raise NotImplementedError()


class ImageModelServiceAbstract(ABC):
    @abstractmethod
    def get_cache_image_url(self, profile: ImageProfileAbstract) -> str | None:
        raise NotImplementedError()

    @abstractmethod
    def upload_image(self, image_path: Path) -> str:
        raise NotImplementedError()


class ImageModelService:
    def get_cache_image_url(self, profile: ImageProfileAbstract) -> str | None:
        raise NotImplementedError()

    def upload_image(self, image_path: Path) -> str:
        raise NotImplementedError()
