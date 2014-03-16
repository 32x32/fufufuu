from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import ugettext as _
from fufufuu.core.views import StaffTemplateView
from fufufuu.staff.forms import SiteSettingForm


class StaffView(StaffTemplateView):

    template_name = 'staff/staff.html'

    def get(self, request):
        return self.render_to_response({
            'form': SiteSettingForm()
        })

    def post(self, request):
        form = SiteSettingForm(data=request.POST)
        if form.is_valid():
            form.save(request.user)
            messages.success(request, _('Site settings have been updated'))
            return redirect('staff')

        return self.render_to_response({
            'form': form,
        })
