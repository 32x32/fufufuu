from django.core.files.uploadedfile import SimpleUploadedFile

from FUBase import FUBase
from fufufuu.manga.models import MangaPage, Manga
from fufufuu.manga.utils import MangaArchiveGenerator
from models import OldMangaPage

#-------------------------------------------------------------------------------

MANGA_ID_LIST = [
    12500,
    12501,
    12502,
    12503,
    12504,
    12505,
    12506,
    12507,
    12508,
    12509,
    12510,
    12511,
    12512,
    12514,
    12515,
    12518,
    12519,
    12520,
    12522,
    12523,
    12525,
    12534,
    12535,
    12536,
    12539,
    12541,
    12544,
    12545,
    12551,
    12552,
    12553,
    12565,
    12567,
    12576,
    12578,
    12579,
    12580,
    12582,
    12583,
]

#-------------------------------------------------------------------------------


class FU217(FUBase):
    """
    This ticket re-migrates the manga pages from the old database. It also
    generates a new manga archive.
    """

    def get_file(self, path):
        if not path: return None
        try:
            return SimpleUploadedFile('migrator', open('{}{}'.format(self.OLD_MEDIA_ROOT, path), mode='rb').read())
        except FileNotFoundError:
            return None

    def remigrate_manga(self, manga_id):
        if MangaPage.objects.filter(manga_id=manga_id).exists():
            return

        for old_manga_page in self.session.query(OldMangaPage).filter(OldMangaPage.manga_id==manga_id):
            MangaPage.objects.create(
                manga_id=manga_id,
                double=old_manga_page.double,
                page=old_manga_page.page,
                image=self.get_file(old_manga_page.image_source),
                name=old_manga_page.name and old_manga_page.name[:100] or '-'
            )

    def run(self):
        for manga_id in MANGA_ID_LIST:
            print('Processing {}'.format(manga_id))
            self.remigrate_manga(manga_id)
            try:
                manga = Manga.published.get(id=manga_id)
                MangaArchiveGenerator.generate(manga)
            except Manga.DoesNotExist as e:
                print('Error {}: {}'.format(manga_id, e))


if __name__ == '__main__':
    FU217().start()
