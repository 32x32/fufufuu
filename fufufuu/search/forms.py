from haystack.forms import SearchForm
from fufufuu.manga.models import Manga
from fufufuu.manga.views import MangaListMixin


class MangaSearchForm(MangaListMixin, SearchForm):

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def search(self):
        if not self.is_valid():
            return self.no_query_found()

        if not self.cleaned_data.get('q'):
            return self.no_query_found()

        filters = self.get_filters()
        query = self.cleaned_data.get('q')
        sqs = self.searchqueryset.models(Manga).filter(**filters).auto_query(query)

        if self.load_all:
            sqs = sqs.load_all()

        return sqs
