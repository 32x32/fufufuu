from FUBase import FUBase
from fufufuu.manga.models import MangaArchive


class FU244(FUBase):
    """
    This script will update the archive names to the new format of

        [Scanlator][Circle (Author)] Title.zip

    """

    def run(self, *args, **kwargs):
        for archive in MangaArchive.objects.order_by('id'):
            archive.name = archive.manga.archive_name
            archive.save()
            print('{} - {}'.format(archive.id, archive.name))


if __name__ == '__main__':
    FU244().start()
