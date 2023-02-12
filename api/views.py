import json
from tempfile import TemporaryDirectory

from dependency_injector.wiring import Provide, inject
from django.http import HttpRequest, HttpResponseBadRequest
from django.shortcuts import redirect

from .containers import Container
from .image_processing import QueryError
from .services import ImageModelServiceAbstract, ImageProcessingServiceAbstract


# Create your views here.
@inject
def get(
    request: HttpRequest,
    image_processing: ImageProcessingServiceAbstract = Provide[
        Container.image_processing_service
    ],
    image_model: ImageModelServiceAbstract = Provide[Container.image_model_service],
):
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
