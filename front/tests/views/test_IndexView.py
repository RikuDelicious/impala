from unittest.mock import patch

from django.test import Client, RequestFactory
from django.urls import reverse

from api.image_processing import ImageProfileForm
from front.views import IndexView

# Stubs
########################################################################################


class ProfileFormStub1(ImageProfileForm):
    @classmethod
    def get_profile_type(cls) -> str:
        return "profile_type_stub1"

    def get_query_string(self) -> str:
        return "query_string_stub1=some_value"

    @classmethod
    def get_description(cls) -> str:
        return "profile_type_stub1_description"


class ProfileFormStub2(ImageProfileForm):
    @classmethod
    def get_profile_type(cls) -> str:
        return "profile_type_stub2"

    def get_query_string(self) -> str:
        return "query_string_stub2=some_value"

    @classmethod
    def get_description(cls) -> str:
        return "profile_type_stub2_description"


# Tests
########################################################################################


def test_access(client: Client):
    with patch(
        "front.views.IndexView.form_classes", new=[ProfileFormStub1, ProfileFormStub2]
    ):
        res = client.get(reverse("front:index"))
        res.status_code == 200


def test_get_context_data(rf: RequestFactory):
    with patch(
        "front.views.IndexView.form_classes", new=[ProfileFormStub1, ProfileFormStub2]
    ):
        req = rf.get(reverse("front:index"))
        view = IndexView()
        view.setup(req)

        context = view.get_context_data()
        assert context["form_links"] == [
            {
                "label": "profile_type_stub1",
                "url": reverse(
                    "front:profile_form", kwargs={"profile_type": "profile_type_stub1"}
                ),
                "description": "profile_type_stub1_description",
            },
            {
                "label": "profile_type_stub2",
                "url": reverse(
                    "front:profile_form", kwargs={"profile_type": "profile_type_stub2"}
                ),
                "description": "profile_type_stub2_description",
            },
        ]
