from django.shortcuts import get_object_or_404
from fufufuu.account.models import User
from fufufuu.core.utils import paginate
from fufufuu.core.views import TemplateView
from fufufuu.manga.models import Manga
from fufufuu.manga.views import MangaListMixin


class UserViewMixin:

    def get_user(self, username):
        return get_object_or_404(User, username=username, is_active=True)


class UserView(UserViewMixin, TemplateView):

    template_name = 'user/user.html'

    def get(self, request, username):
        return self.render_to_response({
            'target_user': self.get_user(username),
        })


class UserUploadsView(UserViewMixin, MangaListMixin, TemplateView):

    template_name = 'user/user-uploads.html'

    def get(self, request, username):
        target_user = self.get_user(username)

        filters = self.get_filters()
        filters['created_by_id'] = target_user.id

        manga_list = Manga.published.filter(**filters).order_by('-published_on')
        manga_list = paginate(manga_list, self.page_size, request.GET.get('p'))

        return self.render_to_response({
            'manga_list': manga_list,
            'target_user': target_user,
        })
