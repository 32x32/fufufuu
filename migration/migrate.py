import datetime
import logging
import os
import sys

import markdown
from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import sessionmaker

from models import *

PROJECT_PATH = os.sep.join(os.path.realpath(__file__).split(os.sep)[:-2])
sys.path.append(PROJECT_PATH)
os.environ['DJANGO_SETTINGS_MODULE'] = 'fufufuu.settings'

from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models.aggregates import Max
from fufufuu.account.models import User
from fufufuu.legacy.models import LegacyTank
from fufufuu.manga.enums import MangaCategory
from fufufuu.manga.models import Manga, MangaFavorite, MangaTag, MangaPage
from fufufuu.tag.enums import TagType
from fufufuu.tag.models import Tag

#-------------------------------------------------------------------------------
# migrator configuration
#-------------------------------------------------------------------------------

CHUNK_SIZE = 1000
OLD_MEDIA_ROOT = '/home/derekkwok/media/'
CONNECTION_STRING = 'postgresql://derekkwok:password@localhost/fufufuu_old'

#-------------------------------------------------------------------------------
# logging configuration
#-------------------------------------------------------------------------------

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

#-------------------------------------------------------------------------------
# helper methods
#-------------------------------------------------------------------------------

def timed(func):
    """
    use @timed to decorate a function that will print out the time it took
    for this function to run.
    """

    def inner(*args, **kwargs):
        logger.debug('{} started'.format(func.__name__).ljust(80, '-'))
        start = datetime.datetime.now()
        result = func(*args, **kwargs)
        finish = datetime.datetime.now()
        logger.debug('{} finished in {}'.format(func.__name__, finish-start).ljust(80, '-'))
        return result
    return inner

#-------------------------------------------------------------------------------


class Migrator(object):

    @timed
    def connect(self):
        self.engine = create_engine(CONNECTION_STRING)
        self.session = sessionmaker(bind=self.engine)()

    @timed
    def disconnect(self):
        self.session.close()

    #---------------------------------------------------------------------------

    def convert_markdown(self, markdown_raw):
        return markdown.markdown(markdown_raw)

    def get_file(self, path):
        if not path: return None
        try:
            return SimpleUploadedFile('migrator', open('{}{}'.format(OLD_MEDIA_ROOT, path), mode='rb').read())
        except FileNotFoundError:
            logger.warn('Missing file {}'.format(path))
            return None

    #---------------------------------------------------------------------------

    @timed
    def migrate_users(self):

        def _migrate_users(old_user_list):
            user_list = []
            for old_user in old_user_list:
                is_moderator = 'MODERATOR' in old_user.permission_flags
                user = User(
                    id=old_user.id,
                    username=old_user.username,
                    password=old_user.password,
                    markdown=old_user.description,
                    html=self.convert_markdown(old_user.description),
                    avatar=self.get_file(old_user.picture),
                    is_moderator=is_moderator,
                    is_staff=old_user.is_staff,
                    is_active=old_user.is_active,
                    created_on=old_user.date_joined,
                    last_login=old_user.last_login,
                )
                user_list.append(user)
            User.objects.bulk_create(user_list)

            for old_user in old_user_list:
                User.objects.filter(id=old_user.id).update(created_on=old_user.date_joined)

        count = self.session.query(OldUser).count()
        for i in range(0, count, CHUNK_SIZE):
            logger.debug('migrated {} users'.format(i))
            _migrate_users(self.session.query(OldUser)[i:i+CHUNK_SIZE])

        logger.debug('migrated {} users'.format(count))
        self.user = User.objects.get(username='ParadigmShift')

    @timed
    def migrate_comments(self):
        pass

    @timed
    def migrate_tags(self):
        def _migrate_tags(old_tag_list):
            tag_list = []
            for old_tag in old_tag_list:
                tag_list.append(Tag(
                    id=old_tag.id,
                    tag_type=old_tag.tag_type,
                    name=old_tag.name,
                    slug=old_tag.slug,
                    created_by_id=self.user.id,
                    created_on=old_tag.date_created,
                ))
            Tag.objects.bulk_create(tag_list)

        count = self.session.query(OldTag).count()
        for i in range(0, count, CHUNK_SIZE):
            logger.debug('migrated {} tags'.format(i))
            _migrate_tags(self.session.query(OldTag)[i:i+CHUNK_SIZE])

        logger.debug('migrated {} tags'.format(count, count))

    @timed
    def migrate_tanks(self):
        new_id = Tag.objects.all().aggregate(Max('id'))['id__max']
        tank_title_map = {}

        for old_tank in self.session.query(OldTank):

            if old_tank.title in tank_title_map:
                LegacyTank.objects.create(id=old_tank.id, tag=tank_title_map[old_tank.title])
                continue

            manga = self.session.query(OldManga).filter(OldManga.tank_id==old_tank.id).order_by(OldManga.tank_chp)[:]
            if len(manga) > 0:
                cover = manga[0].cover
            else:
                cover = None

            new_id += 1
            tag = Tag(
                id=new_id,
                tag_type=TagType.TANK,
                name=old_tank.title,
                slug=old_tank.slug,
                created_by_id=self.user.id,
                created_on=old_tank.date_created,
                cover=self.get_file(cover),
            )
            tag.save(updated_by=None)
            tank_title_map[old_tank.title] = tag

            LegacyTank.objects.create(
                id=old_tank.id,
                tag=tag
            )

        logger.debug('created {} legacy tanks'.format(LegacyTank.objects.all().count()))
        logger.debug('migrated {} tanks'.format(Tag.objects.filter(tag_type=TagType.TANK).count()))

    @timed
    def migrate_manga(self):
        tank_list = LegacyTank.objects.all()
        tank_dict = dict([(t.id, t.tag_id) for t in tank_list])

        def _migrate_manga(old_manga_list):
            manga_list = []
            for old_manga in old_manga_list:
                tank_id = None
                if old_manga.tank_id: tank_id = tank_dict.get(old_manga.tank_id)

                category = old_manga.category
                if category == 'NON-H': category = MangaCategory.NON_H

                language = old_manga.language
                if language == 'zh-cn': language = 'zh'

                manga_list.append(Manga(
                    id=old_manga.id,
                    title=old_manga.title,
                    slug=old_manga.slug,
                    markdown=old_manga.description,
                    html=self.convert_markdown(old_manga.description),
                    cover=self.get_file(old_manga.cover),
                    category=category,
                    status=old_manga.status,
                    language=language,
                    uncensored=False,
                    tank_id=tank_id,
                    tank_chapter=old_manga.tank_chp,
                    published_on=old_manga.date_published,
                    created_by_id=old_manga.uploader_id,
                    updated_on=old_manga.last_updated,
                ))
            Manga.objects.bulk_create(manga_list)

            for old_manga in old_manga_list:
                Manga.objects.filter(id=old_manga.id).update(created_on=old_manga.date_created)

        count = self.session.query(OldManga).count()
        for i in range(0, count, CHUNK_SIZE):
            logger.debug('migrated {} manga'.format(i))
            _migrate_manga(self.session.query(OldManga)[i:i+CHUNK_SIZE])

        logger.debug('migrated {} manga'.format(Manga.all.all().count()))

    @timed
    def migrate_manga_favorites(self):
        def _migrate_manga_favorites(old_manga_favorites_list):
            manga_favorites_list = []
            for old_manga_favorites in old_manga_favorites_list:
                manga_favorites_list.append(MangaFavorite(
                    id=old_manga_favorites.id,
                    manga_id=old_manga_favorites.manga_id,
                    user_id=old_manga_favorites.user_id,
                ))
            MangaFavorite.objects.bulk_create(manga_favorites_list)

        count = self.session.query(OldMangaFavoriteUser).count()
        for i in range(0, count, CHUNK_SIZE):
            logger.debug('migrated {} manga favorites'.format(i))
            _migrate_manga_favorites(self.session.query(OldMangaFavoriteUser)[i:i+CHUNK_SIZE])

        logger.debug('migrated {} manga favorites'.format(MangaFavorite.objects.all().count()))

    @timed
    def migrate_manga_tags(self):
        def _migrate_manga_tags(old_manga_tag_list):
            manga_tag_list = []
            for old_manga_tag in old_manga_tag_list:
                manga_tag_list.append(MangaTag(
                    id=old_manga_tag.id,
                    manga_id=old_manga_tag.manga_id,
                    tag_id=old_manga_tag.tag_id,
                ))
            MangaTag.objects.bulk_create(manga_tag_list)

        count = self.session.query(OldMangaTag).count()
        for i in range(0, count, CHUNK_SIZE):
            logger.debug('migrated {} manga tags'.format(MangaTag.objects.all().count()))
            _migrate_manga_tags(self.session.query(OldMangaTag)[i:i+CHUNK_SIZE])

        logger.debug('migrated {} manga tags'.format(MangaTag.objects.all().count()))

    def migrate_manga_pages(self):
        logger.debug('manga pages migration started'.center(80, '-'))

        def _migrate_manga_pages(old_manga_page_list):
            manga_page_list = []
            for old_manga_page in old_manga_page_list:
                manga_page_list.append(MangaPage(
                    manga_id=old_manga_page.manga_id,
                    double=old_manga_page.double,
                    page=old_manga_page.page,
                    image=self.get_file(old_manga_page.image_source),
                    name=old_manga_page.name and old_manga_page.name[:100] or '',
                ))
            MangaPage.objects.bulk_create(manga_page_list)

        count = self.session.query(OldMangaPage).count()
        for i in range(0, count, CHUNK_SIZE):
            logger.debug('migrated {} manga pages'.format(i))
            _migrate_manga_pages(self.session.query(OldMangaPage)[i:i+CHUNK_SIZE])

        logger.debug('migrated {} manga pages'.format(MangaPage.objects.all().count()))

    @timed
    def run(self):
        self.connect()
        self.migrate_users()
        self.migrate_comments()
        self.migrate_tags()
        self.migrate_tanks()
        self.migrate_manga()
        self.migrate_manga_favorites()
        self.migrate_manga_tags()
        self.migrate_manga_pages()
        self.disconnect()


if __name__ == '__main__':
    migrator = Migrator()
    migrator.run()
