import argparse, datetime, os, random, sys

PROJECT_PATH = os.sep.join(os.path.realpath(__file__).split(os.sep)[:-2])
sys.path.append(PROJECT_PATH)
os.environ['DJANGO_SETTINGS_MODULE'] = 'fufufuu.settings'

from fufufuu.account.models import User
from fufufuu.tag.enums import TagType
from fufufuu.tag.models import Tag, TagData, TagDataHistory

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
        for tag_type, _ in TagType.choices:
            for i in range(1, self.config['TAGS']+1):
                tag_list.append(Tag(tag_type=tag_type))
        Tag.objects.bulk_create(tag_list)

    @timed
    def create_tag_data(self):
        for language in ['en', 'ja']:
            tag_data_list = []
            for tag_type, _ in TagType.choices:
                for i, tag in enumerate(Tag.objects.filter(tag_type=tag_type), start=1):
                    tag_data_list.append(TagData(
                        tag=tag,
                        language=language,
                        name='{} {} - {}'.format(tag_type, i, language),
                        updated_by=self.user
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
                    name=tag_data.name,
                    slug=tag_data.slug,
                    markdown='History {}'.format(i),
                    html='History {}'.format(i),
                    created_by=self.user,
                ))
                i += 1
        TagDataHistory.objects.bulk_create(tdh_list)

    def run(self):
        print('-'*80)
        print('datacreator.py started')
        start = datetime.datetime.now()

        self.create_users()
        self.create_tags()
        self.create_tag_data()
        self.create_tag_data_histories()

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
