from haystack import indexes

from fufufuu.manga.models import Manga


class MangaIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.CharField(document=True, use_template=True)
    category = indexes.CharField(model_attr='category')
    language = indexes.CharField(model_attr='language')
    status = indexes.CharField(model_attr='status')

    def get_model(self):
        return Manga

    def index_queryset(self, using=None):
        return self.get_model().published.select_related('tank', 'collection')
