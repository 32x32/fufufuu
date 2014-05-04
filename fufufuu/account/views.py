from django.contrib.auth import logout, login
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseNotAllowed, Http404
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic.base import View
from fufufuu.account.forms import AccountLoginForm, AccountRegisterForm, AccountSettingsForm, AccountSettingsPasswordForm
from fufufuu.core.enums import SiteSettingKey
from fufufuu.core.models import SiteSetting
from fufufuu.core.views import TemplateView, ProtectedTemplateView
from fufufuu.dmca.forms import DmcaAccountForm


class AccountBaseView(TemplateView):

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect('manga.list')
        return super().dispatch(request, *args, **kwargs)


class AccountLoginView(AccountBaseView):

    template_name = 'account/account-login.html'

    def get(self, request):
        return self.render_to_response({'form': AccountLoginForm(request=request)})

    def post(self, request):
        form = AccountLoginForm(request=request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            next = request.POST.get('next', reverse('manga.list'))
            return redirect(next)

        return self.render_to_response({'form': form})


class AccountRegisterView(AccountBaseView):

    template_name = 'account/account-register.html'

    def get(self, request):
        if not SiteSetting.get_val(SiteSettingKey.ENABLE_REGISTRATION):
            messages.warning(request, _('Account registration at Fufufuu has been disabled.'))

        return self.render_to_response({'form': AccountRegisterForm()})

    def post(self, request):
        if not SiteSetting.get_val(SiteSettingKey.ENABLE_REGISTRATION):
            return redirect('account.register')

        form = AccountRegisterForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            next = request.POST.get('next', reverse('manga.list'))
            return redirect(next)

        return self.render_to_response({'form': form})


class AccountLogoutView(View):

    def get(self, request):
        return HttpResponseNotAllowed(permitted_methods=['post'])

    def post(self, request):
        logout(request)
        return redirect('account.login')


#-------------------------------------------------------------------------------


class AccountSettingsBaseView(ProtectedTemplateView):

    template_name = 'account/account-settings.html'

    def render_to_response(self, context_additional):
        context = {
            'form': AccountSettingsForm(instance=self.request.user),
            'password_form': AccountSettingsPasswordForm(user=self.request.user),
        }
        context.update(context_additional)
        return super().render_to_response(context)

    def get(self, request):
        return self.render_to_response({})


class AccountSettingsView(AccountSettingsBaseView):

    def post(self, request):
        form = AccountSettingsForm(instance=request.user, data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, _('Your profile has been updated.'))
            return redirect('account.settings')

        return self.render_to_response({
            'form': form,
        })


class AccountSettingsPasswordView(AccountSettingsBaseView):

    def post(self, request):
        form = AccountSettingsPasswordForm(user=self.request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _('Your password has been updated.'))
            return redirect('account.settings')

        return self.render_to_response({
            'password_form': form,
        })


class AccountSettingsDmcaView(ProtectedTemplateView):

    template_name = 'account/account-settings-dmca.html'

    def get(self, request):
        if not request.user.dmca_account_id:
            raise Http404

        return self.render_to_response({
            'form': DmcaAccountForm(instance=request.user.dmca_account)
        })

    def post(self, request):
        if not request.user.dmca_account_id:
            raise Http404

        form = DmcaAccountForm(instance=request.user.dmca_account, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _('Your account details have been updated successfully.'))
            return redirect('account.settings.dmca')

        return self.render_to_response({
            'form': form,
        })
