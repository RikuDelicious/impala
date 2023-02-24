from django.http import Http404
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import FormView, TemplateView

from api.services import ImageProcessingService, ImageProfileForm


# Create your views here.
class IndexView(TemplateView):
    template_name = "front/index.html"
    form_classes = ImageProcessingService.form_classes

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_links"] = [
            {
                "label": form_class.get_profile_type(),
                "url": reverse(
                    "front:profile_form",
                    kwargs={"profile_type": form_class.get_profile_type()},
                ),
                "description": form_class.get_description(),
            }
            for form_class in self.form_classes
        ]
        return context


class ProfileFormView(FormView):
    template_name = "front/form.html"
    form_classes = ImageProcessingService.form_classes

    def get_form_class(self):
        for form_class in self.form_classes:
            if self.kwargs["profile_type"] == form_class.get_profile_type():
                return form_class
        raise Http404()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_links"] = [
            {
                "label": form_class.get_profile_type(),
                "url": reverse(
                    "front:profile_form",
                    kwargs={"profile_type": form_class.get_profile_type()},
                ),
                "description": form_class.get_description(),
            }
            for form_class in self.form_classes
        ]
        return context

    def form_valid(self, form: ImageProfileForm):
        query_string = form.get_query_string()
        result_image_url = self.request.build_absolute_uri(
            f"{reverse('api:get')}?{query_string}"
        )

        context = self.get_context_data()
        context["result_image_url"] = result_image_url
        return render(self.request, self.template_name, context)
