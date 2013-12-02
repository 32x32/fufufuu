from django.contrib.auth import logout, login
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseNotAllowed
from django.shortcuts import redirect
from django.views.generic.base import View
from fufufuu.account.forms import AccountLoginForm, AccountRegisterForm
from fufufuu.core.views import TemplateView


class AccountBaseView(TemplateView):

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect('manga.list')
        return super().dispatch(request, *args, **kwargs)


class AccountLoginView(AccountBaseView):

    template_name = 'account/account-login.html'

    def get(self, request):
        return self.render_to_response({'form': AccountLoginForm()})

    def post(self, request):
        form = AccountLoginForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            next = request.POST.get('next', reverse('manga.list'))
            return redirect(next)

        return self.render_to_response({'form': form})


class AccountRegisterView(AccountBaseView):

    template_name = 'account/account-register.html'

    def get(self, request):
        return self.render_to_response({'form': AccountRegisterForm()})

    def post(self, request):
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
