from fufufuu.manga.enums import MangaStatus, MangaCategory


class MangaMixin:

    @property
    def status_display(self): return MangaStatus.choices_dict[self.status]

    @property
    def category_display(self): return MangaCategory.choices_dict[self.category]
