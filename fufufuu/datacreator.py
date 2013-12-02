import argparse, datetime, os, sys

PROJECT_PATH = os.sep.join(os.path.realpath(__file__).split(os.sep)[:-2])
sys.path.append(PROJECT_PATH)
os.environ['DJANGO_SETTINGS_MODULE'] = 'fufufuu.settings'

from fufufuu.account.models import User

#-------------------------------------------------------------------------------

CONFIGURATION = {
    'default': {
        'MANGA': 3000,
        'TAGS': 600,
        'USERS': 5,
    },
    'test': {
        'MANGA': 20,
        'TAGS': 5,
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

    def run(self):
        print('-'*80)
        print('datacreator.py started')
        start = datetime.datetime.now()

        self.create_users()

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
