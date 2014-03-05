import logging
from multiprocessing import Pool
import os
import sys

import markdown
from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import sessionmaker

from models import *


PROJECT_PATH = os.sep.join(os.path.realpath(__file__).split(os.sep)[:-2])
sys.path.append(PROJECT_PATH)
os.environ['DJANGO_SETTINGS_MODULE'] = 'fufufuu.settings'

from django import db
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models.aggregates import Max
from django.db.utils import IntegrityError
from fufufuu.account.models import User
from fufufuu.image.enums import ImageKeyType
from fufufuu.image.models import Image
from fufufuu.legacy.models import LegacyTank
from fufufuu.manga.enums import MangaCategory
from fufufuu.manga.models import Manga, MangaFavorite, MangaTag, MangaPage
from fufufuu.tag.enums import TagType
from fufufuu.tag.models import Tag


CHUNK_SIZE = 1000
OLD_MEDIA_ROOT = '/home/derekkwok/media/'
CONNECTION_STRING = 'postgresql://derekkwok:password@localhost/fufufuu_old'


def process_image_list(l):
    db.close_old_connections()

    pool = Pool()
    pool.starmap(image_resize, l)
    pool.close()
    pool.join()


def image_resize(file_path, key_type, key_id):
    if not os.path.exists(file_path):
        return
    try:
        image = Image(key_type=key_type, key_id=key_id)
        image.save(file_path)
    except IntegrityError:
        pass


class Migrator(object):

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG)

        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)

    def connect(self):
        self.engine = create_engine(CONNECTION_STRING)
        self.session = sessionmaker(bind=self.engine)()

        self.logger.debug('connected to fufufuu_old')

    def disconnect(self):
        self.session.close()
        self.logger.debug('disconnected to fufufuu_old')

    #---------------------------------------------------------------------------

    def convert_markdown(self, markdown_raw):
        return markdown.markdown(markdown_raw)

    def get_file(self, path):
        if not path: return None
        try:
            return SimpleUploadedFile('migrator', open('{}{}'.format(OLD_MEDIA_ROOT, path), mode='rb').read())
        except FileNotFoundError:
            self.logger.warn('Missing file {}'.format(path))
            return None

    #---------------------------------------------------------------------------

    def migrate_users(self):
        self.logger.debug('users migration started'.center(80, '-'))

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

        count = self.session.query(OldUser).count()
        for i in range(0, count, CHUNK_SIZE):
            self.logger.debug('migrated {} users'.format(i))
            _migrate_users(self.session.query(OldUser)[i:i+CHUNK_SIZE])

        self.logger.debug('migrated {} users'.format(User.objects.all().count()))
        self.user = User.objects.get(username='ParadigmShift')

    def migrate_comments(self):
        pass

    def migrate_tags(self):
        self.logger.debug('tag migration started'.center(80, '-'))

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
            self.logger.debug('migrated {} tags'.format(i))
            _migrate_tags(self.session.query(OldTag)[i:i+CHUNK_SIZE])

        self.logger.debug('migrated {} tags'.format(Tag.objects.all().count()))

    def migrate_tanks(self):
        self.logger.debug('tank migration started'.center(80, '-'))

        new_id = Tag.objects.all().aggregate(Max('id'))['id__max']
        tank_title_map = {}

        for old_tank in self.session.query(OldTank):

            if old_tank.title in tank_title_map:
                LegacyTank.objects.create(id=old_tank.id, tag=tank_title_map[old_tank.title])
                continue

            new_id += 1
            tag = Tag(
                id=new_id,
                tag_type=TagType.TANK,
                name=old_tank.title,
                slug=old_tank.slug,
                created_by_id=self.user.id,
                created_on=old_tank.date_created,
            )
            tag.save(updated_by=None)
            tank_title_map[old_tank.title] = tag

            LegacyTank.objects.create(
                id=old_tank.id,
                tag=tag
            )

        self.logger.debug('created {} legacy tanks'.format(LegacyTank.objects.all().count()))
        self.logger.debug('migrated {} tanks'.format(Tag.objects.filter(tag_type=TagType.TANK).count()))


    def migrate_manga(self):
        self.logger.debug('manga migration started'.center(80, '-'))
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
                    created_on=old_manga.date_created,
                    created_by_id=old_manga.uploader_id,
                    updated_on=old_manga.last_updated,
                ))
            Manga.objects.bulk_create(manga_list)

        count = self.session.query(OldManga).count()
        for i in range(0, count, CHUNK_SIZE):
            self.logger.debug('migrated {} manga'.format(i))
            _migrate_manga(self.session.query(OldManga)[i:i+CHUNK_SIZE])

        self.logger.debug('migrated {} manga'.format(Manga.all.all().count()))

    def migrate_manga_favorites(self):
        self.logger.debug('manga favorites migration started'.center(80, '-'))

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
            self.logger.debug('migrated {} manga favorites'.format(i))
            _migrate_manga_favorites(self.session.query(OldMangaFavoriteUser)[i:i+CHUNK_SIZE])

        self.logger.debug('migrated {} manga favorites'.format(MangaFavorite.objects.all().count()))

    def migrate_manga_tags(self):
        self.logger.debug('manga tags migration started'.center(80, '-'))

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
            self.logger.debug('migrated {} manga tags'.format(MangaTag.objects.all().count()))
            _migrate_manga_tags(self.session.query(OldMangaTag)[i:i+CHUNK_SIZE])

        self.logger.debug('migrated {} manga tags'.format(MangaTag.objects.all().count()))

    def migrate_manga_pages(self):
        self.logger.debug('manga pages migration started'.center(80, '-'))

        def _migrate_manga_pages(old_manga_page_list):
            manga_page_list = []
            for old_manga_page in old_manga_page_list:
                manga_page_list.append(MangaPage(
                    manga_id=old_manga_page.manga_id,
                    double=old_manga_page.double,
                    page=old_manga_page.page,
                    image=self.get_file(old_manga_page.image_source),
                    name=old_manga_page.name[:100],
                ))
            MangaPage.objects.bulk_create(manga_page_list)

        count = self.session.query(OldMangaPage).count()
        for i in range(0, count, CHUNK_SIZE):
            self.logger.debug('migrated {} manga pages'.format(i))
            _migrate_manga_pages(self.session.query(OldMangaPage)[i:i+CHUNK_SIZE])

        self.logger.debug('migrated {} manga pages'.format(MangaPage.objects.all().count()))

    def generate_cache_users(self):
        self.logger.debug('generate cache for users - started'.center(80, '-'))

        def _generate_cache(user_list):
            process_list = []
            for user in user_list:
                if not user.avatar: continue
                process_list.append((user.avatar.path, ImageKeyType.ACCOUNT_AVATAR, user.id))
            process_image_list(process_list)

        count = User.objects.all().count()
        for i in range(0, count, CHUNK_SIZE):
            self.logger.debug('generated cache for {} users'.format(i))
            _generate_cache(User.objects.all()[i:i+CHUNK_SIZE])

        self.logger.debug('generated cache for {} users'.format(count))

    def generate_cache_manga(self):
        self.logger.debug('generate cache for manga - started'.center(80, '-'))

        def _generate_cache(manga_list):
            process_list = []
            for manga in manga_list:
                if not manga.cover:
                    self.logger.warning('manga {} has no cover'.format(manga.id))
                    continue
                process_list.append((manga.cover.path, ImageKeyType.MANGA_COVER, manga.id))
                process_list.append((manga.cover.path, ImageKeyType.MANGA_INFO_COVER, manga.id))
            process_image_list(process_list)

        count = Manga.all.all().count()
        for i in range(0, count, CHUNK_SIZE):
            self.logger.debug('generated cache for {} manga'.format(i))
            _generate_cache(Manga.all.all()[i:i+CHUNK_SIZE])

        self.logger.debug('generated cache for {} manga'.format(count))

    def generate_cache_manga_pages(self):
        self.logger.debug('generate cache for manga pages - started'.center(80, '-'))

        def _generate_cache(manga_page_list):
            process_list = []
            for mp in manga_page_list:
                if not mp.image:
                    self.logger.warning('manga page {} has no image'.format(mp.id))
                    continue
                image_key_type = mp.double and ImageKeyType.MANGA_PAGE_DOUBLE or ImageKeyType.MANGA_PAGE
                process_list.append((mp.image.path, image_key_type, mp.id))
                process_list.append((mp.image.path, ImageKeyType.MANGA_THUMB, mp.id))
            process_image_list(process_list)

        count = MangaPage.objects.all().count()
        for i in range(0, count, CHUNK_SIZE):
            self.logger.debug('generated cache for {} manga pages'.format(i))
            _generate_cache(MangaPage.objects.all()[i:i+CHUNK_SIZE])

        self.logger.debug('generated cache for {} manga pages'.format(count))

    def run(self):
        import datetime
        start = datetime.datetime.now()
        self.logger.debug('Starting Migration'.center(80, '-'))

        self.connect()
        self.migrate_users()
        self.generate_cache_users()
        self.migrate_comments()
        self.migrate_tags()
        self.migrate_tanks()
        self.migrate_manga()
        self.generate_cache_manga()
        self.migrate_manga_favorites()
        self.migrate_manga_tags()
        self.migrate_manga_pages()
        self.generate_cache_manga_pages()
        self.disconnect()

        end = datetime.datetime.now()
        self.logger.debug('Finished Migration in {}'.format(end-start).center(80, '-'))

if __name__ == '__main__':
    migrator = Migrator()
    migrator.run()
