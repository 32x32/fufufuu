from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse, Http404
from django.template.context import get_standard_processors
from django.utils.decorators import method_decorator
from django.views.generic.base import View
from fufufuu.core.templates import TEMPLATE_ENV


class TemplateView(View):
    """
    Any view that extends from BaseTemplateView has {{ TEMPLATE_NAME }}
    available to use.
    """

    template_name = None

    def render_to_response(self, context):
        template = TEMPLATE_ENV.get_template(self.template_name)

        context['TEMPLATE_NAME'] = self.template_name.split('/')[-1].split('.')[0]
        for processor in get_standard_processors():
            context.update(processor(self.request))

        response = HttpResponse(content=template.render(**context))
        response.template_name = self.template_name
        return response


class ProtectedTemplateView(TemplateView):
    """
    User is required to login to view the page.
    """

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class ModeratorTemplateView(TemplateView):
    """
    Return HTTP404 if user is not a moderator or staff.
    """

    @method_decorator
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_moderator and not request.user.is_staff:
            raise Http404
        return super().dispatch(request, *args, **kwargs)


class StaffTemplateView(TemplateView):
    """
    Returns HTTP404 if user is not a moderator or staff. This view does not
    redirect user to the login page.
    """

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            raise Http404
        return super().dispatch(request, *args, **kwargs)


#-------------------------------------------------------------------------------


class PageNotFoundView(TemplateView):

    template_name = '404.html'

    def dispatch(self, request, *args, **kwargs):
        response = self.render_to_response({})
        response.status_code = 404
        return response


class ServerErrorView(TemplateView):

    template_name = '500.html'

    def dispatch(self, request, *args, **kwargs):
        response = self.render_to_response({})
        response.status_code = 500
        return response
