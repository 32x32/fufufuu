from fufufuu.manga.enums import MangaCategory, MangaStatus


def manga_category_display(manga_category):
    return MangaCategory.choices_dict[manga_category]


def manga_status_display(manga_status):
    return MangaStatus.choices_dict[manga_status]
