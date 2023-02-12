import json
from tempfile import TemporaryDirectory

from django.http import HttpRequest, HttpResponseBadRequest
from django.shortcuts import redirect

from .image_processing import QueryError
from .services import ImageModelService, ImageProcessingService


# Create your views here.
def get(request: HttpRequest):
    try:
        profile = image_processing.create_profile(request.GET)
    except QueryError as query_error:
        messages = json.dumps(query_error.messages)
        return HttpResponseBadRequest(messages, content_type="application/json")
    except Exception:
        # 500 Internal Error
        raise

    cache_url = image_model.get_cache_image_url(profile)

    if cache_url is not None:
        return redirect(cache_url)
    else:
        with TemporaryDirectory() as temp_dir_name:
            image_path = image_processing.create_image(profile, temp_dir_name)
            image_url = image_model.upload_image(image_path, profile)
        return redirect(image_url)
