from fufufuu.manga.enums import MangaStatus


class MangaDmcaException(Exception):

    def __init__(self, manga):
        assert manga.status == MangaStatus.DMCA
        self.manga = manga
