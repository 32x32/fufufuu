from FUBase import FUBase
from fufufuu.image.enums import ImageKeyType
from fufufuu.image.models import Image
from fufufuu.manga.models import Manga
from fufufuu.tag.enums import TagType
from fufufuu.tag.models import Tag


class FU220(FUBase):
    """
    This ticket fixes the manga covers that are used in tag covers currently.
    It will also have to regenerate new tag covers.
    """

    CHUNK_SIZE = 100

    def fix_chunk(self, tag_list_chunk):
        tag_id_list = [t.id for t in tag_list_chunk]

        # clear out the tag image cache and regenerate the cached covers
        Image.objects.filter(key_type=ImageKeyType.TAG_COVER, key_id__in=tag_id_list).delete()
        for tag in tag_list_chunk:
            print('Tag {}: {}'.format(tag.id, tag.cover_url))

        # clear out corrupted manga covers and regenerate the cached covers
        Image.objects.filter(key_type=ImageKeyType.MANGA_COVER, key_id__in=tag_id_list).delete()
        for manga in Manga.all.filter(id__in=tag_id_list):
            print('Manga {}: {}'.format(manga.id, manga.cover_url))

    def run(self):
        tag_list = Tag.objects.filter(tag_type__in=[TagType.TANK, TagType.COLLECTION]).order_by('id')
        for i in range(0, len(tag_list), self.CHUNK_SIZE):
            self.fix_chunk(tag_list[i:i+self.CHUNK_SIZE])


if __name__ == '__main__':
    FU220().start()
