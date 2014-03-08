from fufufuu.core.utils import paginate
from fufufuu.core.views import TemplateView
from fufufuu.manga.models import Manga
from fufufuu.manga.views import MangaListMixin


class SearchView(MangaListMixin, TemplateView):

    template_name = 'search/search.html'
    page_size = 120

    def get(self, request):
        query = request.GET.get('q')
        if not query: return self.render_to_response({'manga_list': paginate([], self.page_size, request.GET.get('p'))})

        filters = self.get_filters()
        filters['title__icontains'] = query

        manga_list = Manga.published.filter(**filters)
        manga_list = paginate(manga_list, self.page_size, request.GET.get('p'))

        return self.render_to_response({
            'manga_list': manga_list,
        })
