from django.urls import path
from django.views.generic.base import TemplateView

app_name = "front"

urlpatterns = [
    path("", TemplateView.as_view(template_name="front/index.html"), name="index")
]
