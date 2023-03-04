from django.urls import path

from .views import IndexView, ProfileFormView

app_name = "front"

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("<str:profile_type>/", ProfileFormView.as_view(), name="profile_form"),
]
