from django.apps import AppConfig

from . import container


class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "api"

    def ready(self):
        container.wire(packages=["api"])
