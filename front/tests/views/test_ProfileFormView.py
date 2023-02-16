from unittest.mock import patch

import pytest
from django import forms
from django.http import Http404
from django.test import Client, RequestFactory
from django.urls import reverse

from api.image_processing import ImageProfileForm
from front.views import ProfileFormView

# Stubs
########################################################################################


class ProfileFormStub1(ImageProfileForm):
    field1 = forms.IntegerField(min_value=0, max_value=10)

    @classmethod
    def get_profile_type(cls) -> str:
        return "profile_type_stub1"

    def get_query_string(self) -> str:
        return "query_string_stub1=some_value"


class ProfileFormStub2(ImageProfileForm):
    field1 = forms.IntegerField(min_value=0, max_value=10)

    @classmethod
    def get_profile_type(cls) -> str:
        return "profile_type_stub2"

    def get_query_string(self) -> str:
        return "query_string_stub2=some_value"


# Tests
########################################################################################


def test_access(client: Client):
    with patch(
        "front.views.ProfileFormView.form_classes",
        new=[ProfileFormStub1, ProfileFormStub2],
    ):
        res = client.get(
            reverse("front:profile_form", kwargs={"profile_type": "profile_type_stub1"})
        )
        assert res.status_code == 200


def test_get_form_class_valid(rf: RequestFactory):
    with patch(
        "front.views.ProfileFormView.form_classes",
        new=[ProfileFormStub1, ProfileFormStub2],
    ):
        req = rf.get(
            reverse("front:profile_form", kwargs={"profile_type": "profile_type_stub1"})
        )
        view = ProfileFormView()
        view.setup(req, profile_type="profile_type_stub1")

        result = view.get_form_class()
        assert result == ProfileFormStub1


def test_get_form_class_invalid(rf: RequestFactory):
    with patch(
        "front.views.ProfileFormView.form_classes",
        new=[ProfileFormStub1, ProfileFormStub2],
    ):
        req = rf.get(
            reverse(
                "front:profile_form",
                kwargs={"profile_type": "profile_type_not_supported"},
            )
        )
        view = ProfileFormView()
        view.setup(req, profile_type="profile_type_not_supported")

        with pytest.raises(Http404):
            view.get_form_class()


def test_get_context_data(rf: RequestFactory):
    with patch(
        "front.views.ProfileFormView.form_classes",
        new=[ProfileFormStub1, ProfileFormStub2],
    ):
        req = rf.get(
            reverse("front:profile_form", kwargs={"profile_type": "profile_type_stub1"})
        )
        view = ProfileFormView()
        view.setup(req, profile_type="profile_type_stub1")

        context = view.get_context_data()
        assert context["form_links"] == [
            {
                "label": "profile_type_stub1",
                "url": reverse(
                    "front:profile_form", kwargs={"profile_type": "profile_type_stub1"}
                ),
            },
            {
                "label": "profile_type_stub2",
                "url": reverse(
                    "front:profile_form", kwargs={"profile_type": "profile_type_stub2"}
                ),
            },
        ]


def test_post_form_valid(settings, client: Client):
    settings.ALLOWED_HOSTS += ["example.com"]
    with patch(
        "front.views.ProfileFormView.form_classes",
        new=[ProfileFormStub1, ProfileFormStub2],
    ):
        res = client.post(
            reverse(
                "front:profile_form", kwargs={"profile_type": "profile_type_stub1"}
            ),
            data={"field1": 1},
            HTTP_HOST="example.com",
        )

        assert res.status_code == 200
        assert (
            res.context["result_image_url"]
            == f"http://example.com{reverse('api:get')}?query_string_stub1=some_value"
        )


def test_post_form_invalid(client: Client):
    with patch(
        "front.views.ProfileFormView.form_classes",
        new=[ProfileFormStub1, ProfileFormStub2],
    ):
        res = client.post(
            reverse(
                "front:profile_form", kwargs={"profile_type": "profile_type_stub1"}
            ),
            data={"field1": "hoge"},
        )

        assert res.status_code == 200
        assert res.resolver_match.func.view_class == ProfileFormView
        assert res.resolver_match.captured_kwargs == {
            "profile_type": "profile_type_stub1"
        }
        assert res.context["form"].errors != {}
