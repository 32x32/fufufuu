from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect
from django.utils.translation import ugettext as _
from fufufuu.core.views import TemplateView
from fufufuu.staff.forms import SiteSettingForm


class StaffTemplateView(TemplateView):
    """
    Returns HTTP404 if user is not a moderator or staff. This view does not
    redirect user to the login page.
    """

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            raise Http404
        return super().dispatch(request, *args, **kwargs)


class StaffSiteMetricsView(StaffTemplateView):

    template_name = 'staff/staff-site-metrics.html'

    def get(self, request):
        return self.render_to_response({})


class StaffSiteSettingsView(StaffTemplateView):

    template_name = 'staff/staff-site-settings.html'

    def get(self, request):
        return self.render_to_response({
            'form': SiteSettingForm()
        })

    def post(self, request):
        form = SiteSettingForm(data=request.POST)
        if form.is_valid():
            form.save(request.user)
            messages.success(request, _('Site settings have been updated'))
            return redirect('staff.site.settings')

        return self.render_to_response({
            'form': form,
        })
