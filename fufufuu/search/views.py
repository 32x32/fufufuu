from fufufuu.core.utils import paginate
from fufufuu.core.views import TemplateView
from fufufuu.manga.views import MangaListMixin
from fufufuu.search.forms import MangaSearchForm
from fufufuu.search.paginator import MangaSearchResultsPage


class SearchView(MangaListMixin, TemplateView):

    template_name = 'search/search.html'
    page_size = 120

    def get(self, request):
        form = MangaSearchForm(request=request, data=request.GET, load_all=False)
        sqs = form.search()

        manga_list = paginate(sqs, self.page_size, request.GET.get('p', 1))
        manga_list = MangaSearchResultsPage(manga_list)

        return self.render_to_response({
            'manga_list': manga_list,
        })
