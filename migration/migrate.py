from collections import defaultdict
import logging
import os
import sys

import markdown

from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import sessionmaker

from models import OldUser, OldManga, OldMangaFavoriteUser, OldTag, OldMangaTag, OldTank, OldMangaPage


PROJECT_PATH = os.sep.join(os.path.realpath(__file__).split(os.sep)[:-2])
sys.path.append(PROJECT_PATH)
os.environ['DJANGO_SETTINGS_MODULE'] = 'fufufuu.settings'

from fufufuu.account.models import User
from fufufuu.manga.enums import MangaCategory
from fufufuu.manga.models import Manga, MangaFavorite, MangaTag, MangaPage
from fufufuu.tag.enums import TagType
from fufufuu.tag.models import Tag


CHUNK_SIZE = 1000


class Migrator(object):

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG)

        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)

    def convert_markdown(self, markdown_raw):
        return markdown.markdown(markdown_raw)

    def connect(self):
        self.engine = create_engine('postgresql://derekkwok@localhost/fufufuu_old')
        self.session = sessionmaker(bind=self.engine)()

        self.logger.debug('connected to fufufuu_old')

    def disconnect(self):
        self.session.close()
        self.logger.debug('disconnected to fufufuu_old')

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
                    avatar=None,
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
        self.tank_title_map = defaultdict(list)
        self.tank_id_map = {}
        self.logger.debug('tank migration started'.center(80, '-'))

        def _migrate_tanks(old_tank_list):
            tank_list = []
            for old_tank in old_tank_list:
                skip = old_tank.title in self.tank_title_map
                if skip: continue

                self.tank_title_map[old_tank.title] = old_tank.id

                tank_list.append(Tag(
                    tag_type=TagType.TANK,
                    name=old_tank.title,
                    slug=old_tank.slug,
                    created_by_id=self.user.id,
                    created_on=old_tank.date_created,
                ))
            Tag.objects.bulk_create(tank_list)

        count = self.session.query(OldTank).count()
        for i in range(0, count, CHUNK_SIZE):
            self.logger.debug('migrated {} tanks'.format(i))
            _migrate_tanks(self.session.query(OldTank)[i:i+CHUNK_SIZE])

        self.logger.debug('migrated {} tanks'.format(Tag.objects.filter(tag_type=TagType.TANK).count()))

        # generate map from old_tank_id to new tank id
        tag_list = Tag.objects.filter(tag_type=TagType.TANK)
        tag_dict = dict([(t.name, t.id) for t in tag_list])

        for old_tank in self.session.query(OldTank):
            self.tank_id_map[old_tank.id] = tag_dict.get(old_tank.title)

    def migrate_manga(self):
        self.logger.debug('manga migration started'.center(80, '-'))

        def _migrate_manga(old_manga_list):
            manga_list = []
            for old_manga in old_manga_list:
                tank_id = None
                if old_manga.tank_id:
                    tank_id = self.tank_id_map[old_manga.tank_id]

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
                    cover=None,
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
                    image=None,
                    name=old_manga_page.name,
                ))
            MangaPage.objects.bulk_create(manga_page_list)

        count = self.session.query(OldMangaPage).count()
        for i in range(0, count, CHUNK_SIZE):
            self.logger.debug('migrated {} manga pages'.format(i))
            _migrate_manga_pages(self.session.query(OldMangaPage)[i:i+CHUNK_SIZE])

        self.logger.debug('migrated {} manga pages'.format(MangaPage.objects.all().count()))

    def run(self):
        import datetime
        start = datetime.datetime.now()
        self.logger.debug('Starting Migration'.center(80, '-'))

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

        end = datetime.datetime.now()
        self.logger.debug('Finished Migration in {}'.format(start-end).center(80, '-'))

if __name__ == '__main__':
    migrator = Migrator()
    migrator.run()
