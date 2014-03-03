import datetime
import logging
import os
import sys
from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import sessionmaker
from models import OldUser

PROJECT_PATH = os.sep.join(os.path.realpath(__file__).split(os.sep)[:-2])
sys.path.append(PROJECT_PATH)
os.environ['DJANGO_SETTINGS_MODULE'] = 'fufufuu.settings'

from fufufuu.account.models import User
from fufufuu.core.forms import convert_markdown


class Migrator(object):

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG)

        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)

    def connect(self):
        self.engine = create_engine('postgresql://derekkwok@localhost/fufufuu_old')
        self.session = sessionmaker(bind=self.engine)()

        self.logger.debug('connected to fufufuu_old')

    def disconnect(self):
        self.session.close()
        self.logger.debug('disconnected to fufufuu_old')

    def migrate_users(self):
        self.logger.debug('users migration started')

        now = datetime.datetime.now()

        user_list = []
        for old_user in self.session.query(OldUser):
            is_moderator = 'MODERATOR' in old_user.permission_flags
            user = User(
                id=old_user.id,
                username=old_user.username,
                password=old_user.password,
                markdown=old_user.description,
                html=convert_markdown(old_user.description),
                avatar=None,
                is_moderator=is_moderator,
                is_staff=old_user.is_staff,
                is_active=old_user.is_active,
                created_on=old_user.date_joined,
                updated_on=now,
                last_login=old_user.last_login,
            )
            user_list.append(user)

        User.objects.bulk_create(user_list)
        self.logger.debug('migrated {} users'.format(len(user_list)))

    def migrate_users_avatar(self):
        pass

    def migrate_users_html(self):
        pass

    def run(self):
        self.logger.debug('Starting Migration'.center(80, '-'))

        self.connect()
        self.migrate_users()
        self.migrate_users_avatar()
        self.migrate_users_html()
        self.disconnect()

        self.logger.debug('Finished Migration'.center(80, '-'))

if __name__ == '__main__':
    migrator = Migrator()
    migrator.run()
