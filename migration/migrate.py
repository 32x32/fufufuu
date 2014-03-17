import datetime
import logging
import os
import re
import sys

from jinja2.utils import urlize
from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import sessionmaker

from models import *

PROJECT_PATH = os.sep.join(os.path.realpath(__file__).split(os.sep)[:-2])
sys.path.append(PROJECT_PATH)
os.environ['DJANGO_SETTINGS_MODULE'] = 'fufufuu.settings'

from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models.aggregates import Max
from fufufuu.account.models import User
from fufufuu.comment.models import Comment
from fufufuu.core.utils import convert_markdown
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

SQL_ENGINE = create_engine(CONNECTION_STRING)

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

def convert_text_to_markdown(text):
    text = text.replace('\n', '\n\n')
    text = urlize(text)
    text = re.sub(r'<a href="(.*?)">.*?</a>', r'[\1](\1)', text)
    return text


def migration(old_model_cls, new_model_cls, clear=False):
    def wrapper(f):
        def inner(self, *args, **kwargs):
            logger.debug('{} started'.format(f.__name__).ljust(80, '-'))
            start_time = datetime.datetime.now()
            session = sessionmaker(bind=SQL_ENGINE)()
            start = new_model_cls.objects.all().aggregate(Max('id'))['id__max'] or 0

            # remove data that was deleted on the other database
            if clear:
                new_model_cls.objects.all().delete()
            else:
                for i in range(0, start+1, CHUNK_SIZE):
                    old_id_list = set([o.id for o in session.query(old_model_cls.id).filter(old_model_cls.id > i, old_model_cls.id <= i+CHUNK_SIZE)])
                    new_id_list = set(new_model_cls.objects.filter(id__gt=i, id__lte=i+CHUNK_SIZE).values_list('id', flat=True))

                    remove_id_list = new_id_list - old_id_list
                    logger.debug('removing ids: {}'.format(remove_id_list))
                    new_model_cls.objects.filter(id__in=remove_id_list).delete()

            # insert new data
            query = session.query(old_model_cls).filter(old_model_cls.id > start).order_by(old_model_cls.id)
            count = query.count()
            for i in range(0, count, CHUNK_SIZE):
                logger.debug('migrated {} {}'.format(i, old_model_cls.__name__))
                f(self, query[i:i+CHUNK_SIZE])

            logger.debug('migrated {} {}'.format(count, old_model_cls.__name__))
            session.close()
            finish_time = datetime.datetime.now()
            logger.debug('{} finished in {}'.format(f.__name__, finish_time-start_time).ljust(80, '-'))

        return inner
    return wrapper

#-------------------------------------------------------------------------------


class Migrator(object):

    def get_file(self, path):
        if not path: return None
        try:
            return SimpleUploadedFile('migrator', open('{}{}'.format(OLD_MEDIA_ROOT, path), mode='rb').read())
        except FileNotFoundError:
            # logger.warn('Missing file {}'.format(path))
            return None

    #---------------------------------------------------------------------------

    @migration(OldUser, User)
    def migrate_users(self, old_user_list):
        user_list = []
        for old_user in old_user_list:
            is_moderator = 'MODERATOR' in old_user.permission_flags
            markdown = convert_text_to_markdown(old_user.description)
            user = User(
                id=old_user.id,
                username=old_user.username,
                password=old_user.password,
                markdown=markdown,
                html=convert_markdown(markdown),
                avatar=self.get_file(old_user.picture),
                is_moderator=is_moderator,
                is_staff=old_user.is_staff,
                is_active=old_user.is_active,
                last_login=old_user.last_login,
            )
            user_list.append(user)
        User.objects.bulk_create(user_list)

        for old_user in old_user_list:
            User.objects.filter(id=old_user.id).update(created_on=old_user.date_joined)

    @migration(OldComment, Comment)
    def migrate_comments(self, old_comment_list):
        content_type = ContentType.objects.get_for_model(Manga)
        comment_list = []
        for old_comment in old_comment_list:
            markdown = convert_text_to_markdown(old_comment.comment)
            comment_list.append(Comment(
                id=old_comment.id,
                content_type=content_type,
                object_id=old_comment.object_pk,
                markdown=markdown,
                html=convert_markdown(markdown),
                ip_address=old_comment.ip_address,
                created_by_id=old_comment.user_id,
            ))
        Comment.objects.bulk_create(comment_list)

        for old_comment in old_comment_list:
            Comment.objects.filter(id=old_comment.id).update(created_on=old_comment.date_created)

    @migration(OldTag, Tag)
    def migrate_tags(self, old_tag_list):
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

    @migration(OldTank, LegacyTank)
    def migrate_tanks(self, old_tank_list):
        tank_list = Tag.objects.filter(tag_type=TagType.TANK)
        tank_title_map = dict([(t.name, t) for t in tank_list])

        new_id = Tag.objects.all().aggregate(Max('id'))['id__max'] or 5000

        session = sessionmaker(bind=SQL_ENGINE)()

        for old_tank in old_tank_list:
            if old_tank.title in tank_title_map:
                LegacyTank.objects.create(id=old_tank.id, tag=tank_title_map[old_tank.title])
                continue

            manga = session.query(OldManga).filter(OldManga.tank_id==old_tank.id).order_by(OldManga.tank_chp)[:]
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

            LegacyTank.objects.create(id=old_tank.id, tag=tag)

    @migration(OldManga, Manga)
    def migrate_manga(self, old_manga_list):
        tank_list = LegacyTank.objects.all()
        tank_dict = dict([(t.id, t.tag_id) for t in tank_list])

        manga_list = []
        for old_manga in old_manga_list:
            tank_id = None
            if old_manga.tank_id: tank_id = tank_dict.get(old_manga.tank_id)

            category = old_manga.category
            if category == 'NON-H': category = MangaCategory.NON_H

            language = old_manga.language
            if language == 'zh-cn': language = 'zh'

            markdown = convert_text_to_markdown(old_manga.description)
            manga_list.append(Manga(
                id=old_manga.id,
                title=old_manga.title,
                slug=old_manga.slug,
                markdown=markdown,
                html=convert_markdown(markdown),
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

    @migration(OldMangaFavoriteUser, MangaFavorite, clear=True)
    def migrate_manga_favorites(self, old_manga_favorites_list):
        manga_favorites_list = []
        for old_manga_favorites in old_manga_favorites_list:
            manga_favorites_list.append(MangaFavorite(
                id=old_manga_favorites.id,
                manga_id=old_manga_favorites.manga_id,
                user_id=old_manga_favorites.user_id,
            ))
        MangaFavorite.objects.bulk_create(manga_favorites_list)

    @migration(OldMangaTag, MangaTag, clear=True)
    def migrate_manga_tags(self, old_manga_tag_list):
        manga_tag_list = []
        for old_manga_tag in old_manga_tag_list:
            manga_tag_list.append(MangaTag(
                id=old_manga_tag.id,
                manga_id=old_manga_tag.manga_id,
                tag_id=old_manga_tag.tag_id,
            ))
        MangaTag.objects.bulk_create(manga_tag_list)

    @migration(OldMangaPage, MangaPage)
    def migrate_manga_pages(self, old_manga_page_list):
        manga_page_list = []
        for old_manga_page in old_manga_page_list:
            manga_page_list.append(MangaPage(
                id=old_manga_page.id,
                manga_id=old_manga_page.manga_id,
                double=old_manga_page.double,
                page=old_manga_page.page,
                image=self.get_file(old_manga_page.image_source),
                name=old_manga_page.name and old_manga_page.name[:100] or '',
            ))
        MangaPage.objects.bulk_create(manga_page_list)

    def run(self):
        self.migrate_users()
        self.user = User.objects.get(username='ParadigmShift')

        self.migrate_comments()
        self.migrate_tags()
        self.migrate_tanks()
        self.migrate_manga()
        self.migrate_manga_favorites()
        self.migrate_manga_tags()
        self.migrate_manga_pages()


if __name__ == '__main__':
    migrator = Migrator()
    migrator.run()
