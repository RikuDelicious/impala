import json
from tempfile import TemporaryDirectory

from django.http import HttpRequest, HttpResponseBadRequest
from django.shortcuts import redirect
from django.views.generic.base import View

from .image_processing import QueryError
from .services import ImageModelService, ImageProcessingService


# Create your views here.
class GetView(View):
    http_method_names = ["get"]
    image_processing_service = ImageProcessingService
    image_model_service = ImageModelService

    def get(self, request: HttpRequest):
        try:
            profile = self.image_processing_service.create_profile(request.GET)
        except QueryError as query_error:
            messages = json.dumps(query_error.messages)
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
