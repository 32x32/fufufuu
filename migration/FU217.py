import os
import sys

PROJECT_PATH = os.sep.join(os.path.realpath(__file__).split(os.sep)[:-2])
sys.path.append(PROJECT_PATH)
os.environ['DJANGO_SETTINGS_MODULE'] = 'fufufuu.settings'

from django.core.files.uploadedfile import SimpleUploadedFile
from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import sessionmaker
from fufufuu.manga.models import MangaPage
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


class FU217(object):

    CONNECTION_STRING = 'postgresql://derekkwok:password@localhost/fufufuu_old'
    OLD_MEDIA_ROOT = '/var/www/fufufuu2/media/'

    def __init__(self):
        self.session = None

    def start(self):
        self.connect()
        self.run()

    def connect(self):
        SQL_ENGINE = create_engine(self.CONNECTION_STRING)
        self.session = sessionmaker(bind=SQL_ENGINE)()

    def get_file(self, path):
        if not path: return None
        try:
            return SimpleUploadedFile('migrator', open('{}{}'.format(self.OLD_MEDIA_ROOT, path), mode='rb').read())
        except FileNotFoundError:
            return None

    def remigrate_manga(self, manga_id):
        if MangaPage.objects.filter(manga_id=manga_id).exists():
            # this manga has already been fixed
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
            self.remigrate_manga(manga_id)


if __name__ == '__main__':
    FU217().start()
