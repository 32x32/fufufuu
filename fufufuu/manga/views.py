from django.shortcuts import get_object_or_404
from fufufuu.core.utils import paginate
from fufufuu.core.views import TemplateView, ProtectedTemplateView
from fufufuu.manga.models import Manga


class MangaListView(TemplateView):

    template_name = 'manga/manga-list.html'
    page_size = 120

    def get(self, request):
        manga_list = Manga.published.all()
        manga_list = paginate(manga_list, self.page_size, request.GET.get('p'))
        return self.render_to_response({
            'manga_list': manga_list,
        })


class MangaView(TemplateView):

    template_name = 'manga/manga.html'

    def get(self, request, id, slug):
        manga = get_object_or_404(Manga.published, id=id)
        return self.render_to_response({
            'manga': manga,
        })


class MangaHistoryView(TemplateView):

    template_name = 'manga/manga-history.html'

    def get(self, request, id, slug):
        manga = get_object_or_404(Manga.published, id=id)
        return self.render_to_response({
            'manga': manga,
        })


class MangaEditMixin:

    def get_manga(self, id):
        pass



class MangaEditView(MangaEditMixin, ProtectedTemplateView):

    template_name = 'manga/manga-edit.html'

    def get(self, request, id, slug):
        manga = self.get_manga(id)
        return self.render_to_response({
            'manga': manga,
        })


class MangaEditImagesView(MangaEditMixin, ProtectedTemplateView):

    template_name = 'manga/manga-edit-images.html'

    def get(self, request, id, slug):
        manga = self.get_manga(id)
        return self.render_to_response({
            'manga': manga,
        })
