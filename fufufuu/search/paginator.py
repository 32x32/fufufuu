from django.core.paginator import Page

from fufufuu.manga.models import Manga


class MangaSearchResultsPage(Page):
    """
    This class serves two purposes:
        1. reduce the # of queries required to retrieve the objects to 1
        2. return a Manga object when we iterate over the search results
    """

    def __init__(self, page):
        manga_id_list = [item.pk for item in page]
        self.object_list = Manga.published.filter(id__in=manga_id_list)
        self.number = page.number
        self.paginator = page.paginator
