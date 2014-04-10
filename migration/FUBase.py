import os
import sys

PROJECT_PATH = os.sep.join(os.path.realpath(__file__).split(os.sep)[:-2])
sys.path.append(PROJECT_PATH)
os.environ['DJANGO_SETTINGS_MODULE'] = 'fufufuu.settings'

from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import sessionmaker


class FUBase(object):

    CONNECTION_STRING = 'postgresql://derekkwok:password@localhost/fufufuu_old'
    OLD_MEDIA_ROOT = '/var/www/fufufuu2/media/'

    def __init__(self):
        self.session = None

    def start(self, *args, **kwargs):
        self.connect()
        self.run(*args, **kwargs)

    def connect(self):
        SQL_ENGINE = create_engine(self.CONNECTION_STRING)
        self.session = sessionmaker(bind=SQL_ENGINE)()

    def run(self, *args, **kwargs):
        raise NotImplementedError
