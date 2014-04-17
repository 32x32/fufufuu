from FUBase import FUBase
from fufufuu.manga.models import MangaArchive
from models import OldManga
from django.db.models.expressions import F


class FU229(FUBase):
    """
    This ticket will add the manga download count from 2.0.
    """

    def run(self, *args, **kwargs):
        old_manga_list = list(self.session.query(OldManga))
        total = len(old_manga_list)
        for i, old_manga in enumerate(old_manga_list, start=1):
            MangaArchive.objects.filter(manga_id=old_manga.id).update(downloads=F('downloads')+old_manga.download_count)
            print('{}/{} processed'.format(i, total))


if __name__ == '__main__':
    FU229().start()
