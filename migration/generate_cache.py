from multiprocessing import Pool
import os

from django import db

from migrate import Migrator, timed, logger, CHUNK_SIZE
from fufufuu.account.models import User
from fufufuu.image.enums import ImageKeyType
from fufufuu.image.models import Image
from fufufuu.manga.models import Manga, MangaPage
from fufufuu.tag.models import Tag


#-------------------------------------------------------------------------------
# migrator configuration
#-------------------------------------------------------------------------------

CHUNK_SIZE = 1000

#-------------------------------------------------------------------------------
# helper functions
#-------------------------------------------------------------------------------

def process_image_list(l):
    db.close_old_connections()

    pool = Pool()
    pool.starmap(migrate_image_resize, l)
    pool.close()
    pool.join()


def migrate_image_resize(file_path, key_type, key_id):
    if not os.path.exists(file_path):
        return
    if Image.objects.filter(key_type=key_type, key_id=key_id).exists():
        return
    try:
        image = Image(key_type=key_type, key_id=key_id)
        image.save(file_path)
    except Exception as e:
        logger.warn(str(e))

#-------------------------------------------------------------------------------


class CacheGenerator(Migrator):

    @timed
    def generate_cache_users(self):
        def _generate_cache(user_list):
            process_list = []
            for user in user_list:
                if not user.avatar: continue
                process_list.append((user.avatar.path, ImageKeyType.ACCOUNT_AVATAR, user.id))
            process_image_list(process_list)

        count = User.objects.all().count()
        for i in range(0, count, CHUNK_SIZE):
            logger.debug('generated cache for {} users'.format(i))
            _generate_cache(User.objects.all()[i:i+CHUNK_SIZE])

        logger.debug('generated cache for {} users'.format(count))

    @timed
    def generate_cache_tags(self):
        def _generate_cache(tag_list):
            process_list = []
            for tag in tag_list:
                if not tag.cover: continue
                process_list.append((tag.cover.path, ImageKeyType.MANGA_COVER, tag.id))
            process_image_list(process_list)

        count = Tag.objects.all().count()
        for i in range(0, count, CHUNK_SIZE):
            logger.debug('generated cache for {} tags'.format(i))
            _generate_cache(Tag.objects.all()[i:i+CHUNK_SIZE])

        logger.debug('generated cache for {} tags'.format(count))

    @timed
    def generate_cache_manga(self):
        def _generate_cache(manga_list):
            process_list = []
            for manga in manga_list:
                if not manga.cover:
                    logger.warning('manga {} has no cover'.format(manga.id))
                    continue
                process_list.append((manga.cover.path, ImageKeyType.MANGA_COVER, manga.id))
                process_list.append((manga.cover.path, ImageKeyType.MANGA_INFO_COVER, manga.id))
            process_image_list(process_list)

        count = Manga.all.all().count()
        for i in range(0, count, CHUNK_SIZE):
            logger.debug('generated cache for {} manga'.format(i))
            _generate_cache(Manga.all.all()[i:i+CHUNK_SIZE])

        logger.debug('generated cache for {} manga'.format(count))

    @timed
    def generate_cache_manga_pages(self):
        def _generate_cache(manga_page_list):
            process_list = []
            for mp in manga_page_list:
                if not mp.image:
                    logger.warning('manga page {} has no image'.format(mp.id))
                    continue
                image_key_type = mp.double and ImageKeyType.MANGA_PAGE_DOUBLE or ImageKeyType.MANGA_PAGE
                process_list.append((mp.image.path, image_key_type, mp.id))
                process_list.append((mp.image.path, ImageKeyType.MANGA_THUMB, mp.id))
            process_image_list(process_list)

        count = MangaPage.objects.all().count()
        for i in range(0, count, CHUNK_SIZE):
            logger.debug('generated cache for {} manga pages'.format(i))
            _generate_cache(MangaPage.objects.all()[i:i+CHUNK_SIZE])

        logger.debug('generated cache for {} manga pages'.format(count))

    @timed
    def generate_cache(self):
        self.generate_cache_users()
        self.generate_cache_tags()
        self.generate_cache_manga()
        self.generate_cache_manga_pages()


if __name__ == '__main__':
    cg = CacheGenerator()
    cg.run()
