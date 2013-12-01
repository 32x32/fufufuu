from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse
from django.template.context import get_standard_processors
from django.utils.decorators import method_decorator
from django.views.generic.base import View
from fufufuu.core.templates import TEMPLATE_ENV


class TemplateView(View):
    """
    Any view that extends from BaseTemplateView has {{ TEMPLATE_NAME }}
    available to use.
    """

    def render_to_response(self, context):
        template = TEMPLATE_ENV.get_template(self.template_name)

        context['TEMPLATE_NAME'] = self.template_name.split('/')[-1].split('.')[0]
        for processor in get_standard_processors():
            context.update(processor(self.request))

        response = HttpResponse(content=template.render(**context))
        response.template_name = self.template_name
        return response


class ProtectedTemplateView(TemplateView):

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ProtectedTemplateView, self).dispatch(request, *args, **kwargs)
