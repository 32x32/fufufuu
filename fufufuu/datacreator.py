import argparse
import datetime
import os
import random
import sys
from collections import defaultdict

PROJECT_PATH = os.sep.join(os.path.realpath(__file__).split(os.sep)[:-2])
sys.path.append(PROJECT_PATH)
os.environ['DJANGO_SETTINGS_MODULE'] = 'fufufuu.settings'

from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.webdesign import lorem_ipsum
from fufufuu.comment.models import Comment
from fufufuu.blog.models import BlogEntry
from fufufuu.account.models import User
from fufufuu.core.languages import Language
from fufufuu.core.enums import SiteSettingKey
from fufufuu.core.models import SiteSetting
from fufufuu.core.utils import slugify, convert_markdown
from fufufuu.dmca.models import DmcaAccount
from fufufuu.manga.enums import MangaCategory, MangaStatus
from fufufuu.manga.models import Manga, MangaTag, MangaPage
from fufufuu.report.enums import ReportStatus, ReportMangaType
from fufufuu.report.models import ReportManga
from fufufuu.tag.enums import TagType
from fufufuu.tag.models import Tag, TagData, TagAlias

#-------------------------------------------------------------------------------

CONFIGURATION = {
    'default': {
        'BLOG': 30,
        'COMMENTS': [0, 0, 0, 0, 0, 1, 2, 3],
        'MANGA': 3000,
        'REPORTS': 300,
        'TAGS': 600,
        'TAGS_FK': 30,
        'USERS': 5,
    },
    'test': {
        'BLOG': 1,
        'COLLECTIONS': 1,
        'COMMENTS': [1],
        'MANGA': 1,
        'REPORTS': 1,
        'TAGS': 1,
        'TAGS_FK': 1,
        'USERS': 1,
    }
}

CHUNK_SIZE = 100

#-------------------------------------------------------------------------------

def timed(func):
    """
    use @timed to decorate a function that will print out the time it took
    for this function to run.
    """

    def inner(*args, **kwargs):
        start = datetime.datetime.now()
        result = func(*args, **kwargs)
        finish = datetime.datetime.now()
        print('\t{} - {}'.format(func.__name__, finish-start))
        return result
    return inner

#-------------------------------------------------------------------------------

class DataCreator:

    def __init__(self, configuration):
        self.config = CONFIGURATION[configuration]

    @timed
    def create_users(self):
        def create_user_helper(username, **kwargs):
            user_data = {'username': username}
            user_data.update(**kwargs)
            user = User(**user_data)
            user.set_password('password')
            user.save()
            return user

        self.user = create_user_helper('testuser', is_staff=True, is_moderator=True)
        self.user.dmca_account = DmcaAccount.objects.create(
            name='Sample DMCA Account',
            email='dmca@example.com',
            website='http://example.com/dmca',
        )

        for i in range(self.config['USERS']):
            create_user_helper('testuser{}'.format(i))

    @timed
    def create_tags(self):
        tag_list = []
        for tag_type in TagType.manga_m2m:
            for i in range(1, self.config['TAGS']+1):
                name = '{} {}'.format(TagType.choices_dict[tag_type], i)
                tag = Tag(tag_type=tag_type, name=name, slug=slugify(name), created_by=self.user, updated_by=self.user)
                tag_list.append(tag)
        Tag.objects.bulk_create(tag_list)

    @timed
    def create_tag_aliases(self):
        tag_alias_list = []
        for tag in Tag.objects.all():
            i = 1
            while random.random() < 0.2:
                language = random.choice([Language.ENGLISH, Language.JAPANESE])
                tag_alias = TagAlias(tag=tag, language=language, name='{} - Alias {}'.format(tag.name, i))
                tag_alias_list.append(tag_alias)
                i += 1
        TagAlias.objects.bulk_create(tag_alias_list)

    @timed
    def create_tag_data(self):
        for language in ['en', 'ja']:
            tag_data_list = []
            for tag in Tag.objects.all():
                tag_data_list.append(TagData(
                    tag=tag,
                    language=language,
                    markdown='Tag Data - {} - {}'.format(tag.name, language),
                    html='Tag Data - {} - {}'.format(tag.name, language),
                    created_by=self.user,
                    updated_by=self.user,
                ))
            TagData.objects.bulk_create(tag_data_list)

    @timed
    def create_manga(self):
        manga_category_keys = list(MangaCategory.choices_dict)
        manga_list = []
        for i in range(1, self.config['MANGA']+1):
            title = 'Test Manga {}'.format(i)
            manga = Manga(
                title=title,
                slug=slugify(title),
                status=MangaStatus.PUBLISHED,
                category=random.choice(manga_category_keys),
                language=random.choice(['en'] * 9 + ['ja'] * 1),
                uncensored=random.random() < 0.05,
                published_on=timezone.now(),
                created_by=self.user,
                updated_by=self.user,
            )
            manga_list.append(manga)

        Manga.objects.bulk_create(manga_list)

        two_days_ago = timezone.now() - timezone.timedelta(days=2)
        Manga.objects.update(created_on=two_days_ago, updated_on=two_days_ago, published_on=two_days_ago)

    @timed
    def assign_manga_tank(self):
        manga_id_set = set(Manga.published.all().values_list('id', flat=True))
        for i in range(1, self.config['TAGS_FK']+1):
            tank_name = 'Tank {}'.format(i)
            tank = Tag(tag_type=TagType.TANK, name=tank_name, slug=slugify(tank_name), created_by=self.user, updated_by=self.user)
            tank.save(self.user)

            tank_manga_count = random.randint(1, min(12, len(manga_id_set)))
            tank_manga_id_set = random.sample(manga_id_set, tank_manga_count)

            chapter_dict = defaultdict(int)

            for manga_id in tank_manga_id_set:
                manga = Manga.objects.get(id=manga_id)
                chapter_dict[manga.language] += 1

                manga.tank = tank
                manga.tank_chapter = chapter_dict[manga.language]
                manga.save(updated_by=manga.updated_by)

                manga_id_set.remove(manga_id)

    @timed
    def assign_manga_collection(self):
        manga_id_set = set(Manga.published.all().values_list('id', flat=True))
        for i in range(1, self.config['TAGS_FK']+1):
            collection_name = 'Collection {}'.format(i)
            collection = Tag(tag_type=TagType.COLLECTION, name=collection_name, slug=slugify(collection_name), created_by=self.user, updated_by=self.user)
            collection.save(self.user)

            tank_manga_count = random.randint(1, min(12, len(manga_id_set)))
            tank_manga_id_set = random.sample(manga_id_set, tank_manga_count)

            part_dict = defaultdict(int)

            for manga_id in tank_manga_id_set:
                manga = Manga.objects.get(id=manga_id)
                part_dict[manga.language] += 1

                manga.collection = collection
                manga.collection_part = part_dict[manga.language]
                manga.save(updated_by=manga.updated_by)

                manga_id_set.remove(manga_id)

    @timed
    def create_manga_tags(self):
        tag_dict = defaultdict(list)
        for tag in Tag.objects.all():
            tag_dict[tag.tag_type].append(tag)

        tag_content_count = len(tag_dict[TagType.CONTENT])

        def _create_manga_tags(manga_list):
            manga_tag_list = []
            for manga in manga_list:
                tag_list = []
                for tag_type in [TagType.AUTHOR, TagType.CIRCLE, TagType.EVENT, TagType.MAGAZINE, TagType.PARODY, TagType.SCANLATOR]:
                    if random.random() < 0.5: tag_list.append(random.choice(tag_dict[tag_type]))
                tag_list.extend(random.sample(tag_dict[TagType.CONTENT], random.randint(1, min(10, tag_content_count))))
                manga_tag_list.extend(map(lambda tag: MangaTag(manga=manga, tag=tag), tag_list))
            MangaTag.objects.bulk_create(manga_tag_list)

        for i in range(0, Manga.objects.count(), CHUNK_SIZE):
            _create_manga_tags(Manga.objects.all()[i:i+CHUNK_SIZE])

    @timed
    def create_manga_pages(self):
        manga_page_list = []
        for manga in Manga.objects.all():
            manga_page_list.append(MangaPage(
                manga=manga,
                page=1,
                name='001.jpg',
            ))
        MangaPage.objects.bulk_create(manga_page_list)

    @timed
    def create_comments(self):
        user_list = User.objects.all()
        comment_list = []
        for manga in Manga.published.all():
            for i in range(random.choice(self.config['COMMENTS'])):
                comment = lorem_ipsum.words(random.randint(1, 15), common=False)
                comment_list.append(Comment(
                    content_type=ContentType.objects.get_for_model(manga),
                    object_id=manga.id,
                    markdown=comment,
                    html='<p>{}</p>'.format(comment),
                    created_by=random.choice(user_list),
                ))

        Comment.objects.bulk_create(comment_list)

    @timed
    def create_manga_reports(self):
        user_id_list = User.objects.all().values_list('id', flat=True)
        manga_id_list = Manga.objects.all().values_list('id', flat=True)[:self.config['REPORTS']]
        type_list = list(ReportMangaType.choices_dict.keys())

        report_manga_list = []
        for i in range(self.config['REPORTS']):
            report_manga_list.append(ReportManga(
                manga_id=random.choice(manga_id_list),
                status=ReportStatus.OPEN,
                type=random.choice(type_list),
                comment=lorem_ipsum.sentence(),
                weight=random.randint(1, 25),
                created_by_id=random.choice(user_id_list),
            ))

        ReportManga.all.bulk_create(report_manga_list)

    @timed
    def create_blog_entries(self):
        blog_entry_list = []
        for i in range(self.config['BLOG']):
            title = lorem_ipsum.sentence()
            markdown = '\n\n'.join(lorem_ipsum.paragraphs(random.randint(1, 3)))
            blog_entry = BlogEntry(
                title=title,
                slug=slugify(title),
                markdown=markdown,
                html=convert_markdown(markdown),
                created_by=self.user,
            )
            blog_entry_list.append(blog_entry)

        BlogEntry.objects.bulk_create(blog_entry_list)

    @timed
    def create_settings(self):
        settings = (
            (SiteSettingKey.ENABLE_COMMENTS, 'True'),
            (SiteSettingKey.ENABLE_DOWNLOADS, 'True'),
            (SiteSettingKey.ENABLE_REGISTRATION, 'True'),
            (SiteSettingKey.ENABLE_UPLOADS, 'True'),
        )
        for k, v in settings: SiteSetting.set_val(k, v, self.user)

    def run(self):
        print('-'*80)
        print('datacreator.py started')
        start = datetime.datetime.now()

        self.create_users()
        self.create_tags()
        self.create_tag_aliases()
        self.create_tag_data()
        self.create_manga()
        self.assign_manga_tank()
        self.assign_manga_collection()
        self.create_manga_tags()
        self.create_manga_pages()
        self.create_comments()
        self.create_manga_reports()
        self.create_blog_entries()
        self.create_settings()

        finish = datetime.datetime.now()
        print('datacreator.py finished in {}'.format(finish-start))
        print('-'*80)

#-------------------------------------------------------------------------------

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Datacreator utility for Fufufuu')
    parser.add_argument('--config', dest='config', default='default', help='specify the configuration for datacreator to use (optional)')
    arg_dict = vars(parser.parse_args())

    dc = DataCreator(arg_dict['config'])
    dc.run()
