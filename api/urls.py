from django.urls import path

from . import views

app_name = "api"

urlpatterns = [path("get/", views.GetView.as_view(), name="get")]
