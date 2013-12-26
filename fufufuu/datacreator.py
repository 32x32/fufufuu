import argparse, datetime, os, random, sys
from collections import defaultdict

PROJECT_PATH = os.sep.join(os.path.realpath(__file__).split(os.sep)[:-2])
sys.path.append(PROJECT_PATH)
os.environ['DJANGO_SETTINGS_MODULE'] = 'fufufuu.settings'

from django.utils import timezone
from fufufuu.account.models import User
from fufufuu.core.languages import Language
from fufufuu.core.utils import slugify
from fufufuu.manga.enums import MangaCategory, MangaStatus
from fufufuu.manga.models import Manga, MangaTag, MangaHistory, MangaHistoryTag
from fufufuu.tag.enums import TagType
from fufufuu.tag.models import Tag, TagData, TagDataHistory, TagHistory, TagAlias

#-------------------------------------------------------------------------------

CONFIGURATION = {
    'default': {
        'MANGA': 3000,
        'TAGS': 600,
        'USERS': 5,
    },
    'test': {
        'MANGA': 1,
        'TAGS': 1,
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
        def create_user_helper(username, is_staff=False):
            user = User(username=username, is_staff=is_staff)
            user.set_password('password')
            user.save()
            return user

        self.user = create_user_helper('testuser', is_staff=True)

        for i in range(self.config['USERS']):
            create_user_helper('testuser{}'.format(i))

    @timed
    def create_tags(self):
        tag_list = []
        for tag_type in TagType.choices_dict:
            for i in range(1, self.config['TAGS']+1):
                name = '{} {}'.format(TagType.choices_dict[tag_type], i)
                tag = Tag(tag_type=tag_type, name=name, slug=slugify(name), created_by=self.user, updated_by=self.user)
                tag_list.append(tag)
        Tag.objects.bulk_create(tag_list)

    @timed
    def create_tag_histories(self):
        tag_history_list = []
        for tag in Tag.objects.all():
            i = 1
            while random.random() < 0.5:
                tag_history = TagHistory(tag=tag, name='{} - History {}'.format(tag.name, i))
                tag_history_list.append(tag_history)
                i += 1
        TagHistory.objects.bulk_create(tag_history_list)

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
    def create_tag_data_histories(self):
        tdh_list = []
        for tag_data in TagData.objects.all():
            i = 1
            while random.random() < 0.3:
                tdh_list.append(TagDataHistory(
                    tag_data=tag_data,
                    markdown='History {}'.format(i),
                    html='History {}'.format(i),
                    created_by=self.user,
                    created_on=timezone.now(),
                ))
                i += 1
        TagDataHistory.objects.bulk_create(tdh_list)

    @timed
    def create_manga(self):
        tank_list = Tag.objects.filter(tag_type=TagType.TANK)
        collection_list = Tag.objects.filter(tag_type=TagType.COLLECTION)

        tank_chapter = defaultdict(int)
        collection_part = defaultdict(int)

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
            if random.random() < 0.1:
                manga.tank = random.choice(tank_list)
                manga.tank_chapter = tank_chapter[manga.tank.id] + 1
            if random.random() < 0.1:
                manga.collection = random.choice(collection_list)
                manga.collection_part = collection_part[manga.collection.id] + 1
            manga_list.append(manga)

        Manga.objects.bulk_create(manga_list)

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
    def create_manga_history(self):
        manga_history_list = []
        for manga in Manga.objects.all():
            i = 1
            while random.random() < 0.3:
                manga_history_list.append(MangaHistory(
                    manga=manga,
                    title=manga.title,
                    slug=manga.slug,
                    markdown='History {}'.format(i),
                    html='History {}'.format(i),
                    created_by=self.user,
                    created_on=timezone.now(),
                ))
                i += 1

        MangaHistory.objects.bulk_create(manga_history_list)

    @timed
    def create_manga_history_tags(self):
        tag_dict = defaultdict(list)
        for tag in Tag.objects.all():
            tag_dict[tag.tag_type].append(tag)

        tag_content_count = len(tag_dict[TagType.CONTENT])

        manga_history_tag_list = []
        for manga_history in MangaHistory.objects.all():
            tag_list = []
            for tag_type in [TagType.AUTHOR, TagType.CIRCLE, TagType.EVENT, TagType.MAGAZINE, TagType.PARODY, TagType.SCANLATOR]:
                if random.random() < 0.5: tag_list.append(random.choice(tag_dict[tag_type]))
            tag_list.extend(random.sample(tag_dict[TagType.CONTENT], random.randint(1, min(10, tag_content_count))))
            manga_history_tag_list.extend(map(lambda tag: MangaHistoryTag(mangahistory=manga_history, tag=tag), tag_list))

        MangaHistoryTag.objects.bulk_create(manga_history_tag_list)

    def run(self):
        print('-'*80)
        print('datacreator.py started')
        start = datetime.datetime.now()

        self.create_users()
        self.create_tags()
        self.create_tag_histories()
        self.create_tag_aliases()
        self.create_tag_data()
        self.create_tag_data_histories()
        self.create_manga()
        self.create_manga_tags()
        self.create_manga_history()
        self.create_manga_history_tags()

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
