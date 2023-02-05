from unittest.mock import patch

import pytest
from django import forms
from django.http import QueryDict

from api.image_processing import ImageProfileAbstract, ImageProfileForm, QueryError
from api.services import ImageProcessingService


class ImageProfileStub(ImageProfileAbstract):
    pass


class ImageProfileFormStub(ImageProfileForm):
    intfield = forms.IntegerField()

    def get_profile(self) -> ImageProfileAbstract:
        return ImageProfileFormStub()


def test_create_file_query_valid():
    service = ImageProcessingService()
    form = ImageProfileFormStub({"intfield": 1})
    querydict = QueryDict()
    with patch.object(service, "route_querydict", return_value=form):
        result = service.create_profile(querydict)
        assert isinstance(result, ImageProfileFormStub)


def test_create_file_query_invalid():
    service = ImageProcessingService()
    form = ImageProfileFormStub({"intfield": "hoge"})
    querydict = QueryDict()
    with patch.object(service, "route_querydict", return_value=form):
        with pytest.raises(QueryError) as exc_info:
            service.create_profile(querydict)
        assert exc_info.value.messages == dict(form.errors)
