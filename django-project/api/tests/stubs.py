from __future__ import annotations

import PIL.Image
from api.image_processing import ImageProfileAbstract


class ImageProfileStub(ImageProfileAbstract):
    def create_pil_image(self) -> PIL.Image.Image:
        raise NotImplementedError()

    @property
    def quality(self) -> int | None:
        raise NotImplementedError()

    @property
    def upload_file_name(self) -> str:
        raise NotImplementedError()

    @classmethod
    def get_extension(cls) -> str:
        raise NotImplementedError()

    def dump_signiture(self) -> str:
        raise NotImplementedError()
