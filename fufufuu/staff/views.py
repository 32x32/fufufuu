from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, get_object_or_404
from django.utils.translation import ugettext as _
from fufufuu.account.models import User
from fufufuu.core.utils import paginate
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


class StaffDmcaAccountListView(StaffTemplateView):

    page_size = 100
    template_name = 'staff/staff-dmca-account-list.html'

    def get(self, request):
        user_list = User.objects.filter(dmca_account__isnull=False).select_related('dmca_account')
        user_list = paginate(user_list, self.page_size, request.GET.get('p'))
        return self.render_to_response({
            'user_list': user_list,
        })


class StaffDmcaAccountView(StaffTemplateView):

    page_size = 100
    template_name = 'staff/staff-dmca-account.html'

    def get(self, request, id):
        target_user = get_object_or_404(User, id=id)
        return self.render_to_response({
            'target_user': target_user,
        })
