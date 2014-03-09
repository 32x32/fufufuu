from django.shortcuts import get_object_or_404
from fufufuu.account.models import User
from fufufuu.core.views import TemplateView


class UserViewMixin:

    def get_user(self, username):
        return get_object_or_404(User, username=username, is_active=True)


class UserView(UserViewMixin, TemplateView):

    template_name = 'user/user.html'

    def get(self, request, username):
        return self.render_to_response({
            'target_user': self.get_user(username),
        })


class UserUploadsView(UserViewMixin, TemplateView):

    template_name = 'user/user-uploads.html'

    def get(self, request, username):
        return self.render_to_response({
            'target_user': self.get_user(username),
        })
