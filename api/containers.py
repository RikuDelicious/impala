from dependency_injector import containers, providers

from .services import ImageModelService, ImageProcessingService


class Container(containers.DeclarativeContainer):
    image_processing_service = providers.Singleton(ImageProcessingService)
    image_model_service = providers.Singleton(ImageModelService)
