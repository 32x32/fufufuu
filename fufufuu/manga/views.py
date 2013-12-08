from fufufuu.core.utils import paginate
from fufufuu.core.views import TemplateView
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
