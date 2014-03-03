from sqlalchemy.engine import create_engine


class Migrator(object):

    def connect(self):
        engine = create_engine('postgresql://derekkwok@localhost/fufufuu_old')


    def run(self):
        self.connect()

if __name__ == '__main__':
    migrator = Migrator()
    migrator.run()
