import json
from tempfile import TemporaryDirectory
from typing import Type

from django.http import HttpRequest, HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic.base import View
from django_ratelimit.decorators import ratelimit

from .image_processing import QueryError
from .services import (
    ImageModelService,
    ImageModelServiceAbstract,
    ImageProcessingService,
    ImageProcessingServiceAbstract,
)


# Create your views here.
def ratelimited_error(request, exception):
    return JsonResponse({"error": "ratelimited"}, status=429)


class GetView(View):
    http_method_names = ["get"]
    image_processing_service: Type[
        ImageProcessingServiceAbstract
    ] = ImageProcessingService
    image_model_service: Type[ImageModelServiceAbstract] = ImageModelService

    @method_decorator(ratelimit(key="ip", rate="50/s", method="GET"))
    @method_decorator(ratelimit(key="ip", rate="500/m", method="GET"))
    def get(self, request: HttpRequest):
        try:
            profile = self.image_processing_service.create_profile(request.GET)
        except QueryError as query_error:
            messages = json.dumps(query_error.messages, ensure_ascii=False)
            return HttpResponseBadRequest(messages, content_type="application/json")
        except Exception:
            # 500 Internal Error
            raise

        cache_url = self.image_model_service.get_cache_image_url(profile)

        if cache_url is not None:
            return redirect(cache_url)
        else:
            with TemporaryDirectory() as temp_dir_name:
                image_path = self.image_processing_service.create_image(
                    profile, temp_dir_name
                )
                image_url = self.image_model_service.upload_image(image_path, profile)
            return redirect(image_url)
