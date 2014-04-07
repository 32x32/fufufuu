from contextlib import contextmanager

from fabric.api import env
from fabric.context_managers import cd, prefix
from fabric.contrib.console import confirm
from fabric.contrib.files import append, exists
from fabric.contrib.project import rsync_project
from fabric.operations import prompt, sudo, local, run, put, get


#-------------------------------------------------------------------------------
# env settings
#-------------------------------------------------------------------------------

env.use_ssh_config      = True

env.checkout_path       = '/tmp/django'
env.deploy_path         = '/var/www/fufufuu'
env.django_path         = '/var/www/fufufuu/django'
env.media_path          = '/var/www/fufufuu/media'.format(**env)
env.static_path         = '/var/www/fufufuu/static'.format(**env)

env.venv_path           = '/var/www/fufufuu/venv'
env.activate            = 'source /var/www/fufufuu/venv/bin/activate'

#-------------------------------------------------------------------------------
# hosts
#-------------------------------------------------------------------------------

def staging():
    """
    use fufufuu-staging as host
    """

    env.hosts = ['fufufuu-staging']
    env.config = 'staging'


def production():
    """
    use fufufuu as host (note: this is production)
    """

    env.hosts = ['fufufuu3']
    env.config = 'production'

#-------------------------------------------------------------------------------
# activate virtualenv
#-------------------------------------------------------------------------------

@contextmanager
def virtualenv():
    with cd(env.venv_path):
        with prefix(env.activate):
            yield

#-------------------------------------------------------------------------------
# methods
#-------------------------------------------------------------------------------

def install_python():
    """
    builds and installs python
    """

    VERSION = '3.3.5'

    run('wget http://legacy.python.org/ftp//python/{VERSION}/Python-{VERSION}.tgz'.format(VERSION=VERSION))
    run('tar xvf ./Python-{VERSION}.tgz'.format(VERSION=VERSION))
    with cd('./Python-{VERSION}'.format(VERSION=VERSION)):
        sudo('rm -fr /opt/python3.3')
        run('./configure --prefix=/opt/python3.3 --with-bz2')
        run('make')
        sudo('make install')
        sudo('rm -f /usr/local/bin/python3.3')
        sudo('ln -s /opt/python3.3/bin/python3.3 /usr/local/bin/python3.3')
    sudo('rm -f Python-{VERSION}.tgz'.format(VERSION=VERSION))
    sudo('rm -fr Python-{VERSION}'.format(VERSION=VERSION))


def install_elasticsearch():
    """
    installs Elastic Search
    """

    sudo('apt-get update')
    sudo('apt-get -y install python-software-properties')
    sudo('add-apt-repository -y ppa:webupd8team/java')
    sudo('apt-get update')
    sudo('apt-get -y install oracle-java7-installer', pty=False)
    sudo('wget https://download.elasticsearch.org/elasticsearch/elasticsearch/elasticsearch-1.0.1.deb')
    sudo('dpkg -i elasticsearch-1.0.1.deb')


def setup():
    """
    installs all necessary software for fufufuu
    """

    packages = [
        # python
        'build-essential', 'python-dev', 'python-pip',
        # python 3
        'libsqlite3-dev', 'sqlite3', 'bzip2', 'libbz2-dev',
        # database
        'postgresql-9.3', 'postgresql-server-dev-9.3',
        # image processing
        'libjpeg8-dev', 'libpng12-dev', 'libfreetype6-dev',
        # nodejs + memcached
        'nodejs', 'memcached',
        # utilities
        'cron', 'ntp', 'rsync', 'gettext', 'htop', 'tmux', 'bmon',
        # server
        'nginx', 'exim4',
    ]

    db_password = prompt('Please enter the db password: ')

    # setup environment variables
    append('/etc/environment', 'FUFUFUU_DB_PASSWORD="{}"'.format(db_password), use_sudo=True)

    # create directories
    sudo('mkdir -p {deploy_path}/logs'.format(**env))
    sudo('mkdir -p {django_path}/static'.format(**env))
    sudo('mkdir -p {static_path}'.format(**env))
    sudo('mkdir -p {media_path}'.format(**env))
    sudo('touch {django_path}/static/maintenance.html'.format(**env))
    sudo('chown -R www-data:www-data {deploy_path}'.format(**env))
    sudo('chmod 777 /mnt')

    sudo('apt-get update')
    sudo('apt-get install -y python-software-properties')

    # add ppa for nodejs
    sudo('apt-add-repository -y ppa:chris-lea/node.js')

    # add ppa for postgres
    append('/etc/apt/sources.list.d/pgdg.list', 'deb http://apt.postgresql.org/pub/repos/apt/ precise-pgdg main', use_sudo=True)
    sudo('wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -')

    # add ppa for nginx
    sudo('add-apt-repository -y ppa:nginx/stable')

    # apt-get install packages
    sudo('apt-get update')
    sudo('apt-get install -y --force-yes {}'.format(' '.join(packages)))

    if not exists('/usr/local/bin/python3.3'): install_python()

    sudo('pip install supervisor==3.0 awscli==1.3.4')
    sudo('pip install virtualenv')
    sudo('virtualenv {venv_path} --python=/usr/local/bin/python3.3'.format(**env), user='www-data')
    run('aws configure')


#-------------------------------------------------------------------------------
# deploy
#-------------------------------------------------------------------------------


def deploy(tag='master'):
    """
    deploy fufufuu
    """

    _checkout(tag)
    _compile_static()
    _fabric_marker(tag)
    stop()
    _rsync()
    _install_requirements()
    _syncdb_migrate()
    start()
    _install_crontab()

#-------------------------------------------------------------------------------

def _checkout(tag):
    """
    checkout source locally
    """

    local('rm -fr {checkout_path}'.format(**env))
    local('mkdir -p {checkout_path}'.format(**env))
    local('git archive {tag} | tar -x -C {checkout_path}'.format(tag=tag, checkout_path=env.checkout_path))


def _compile_static():
    """
    compiles js and css files
    """

    local('cd {checkout_path} && python scripts/less.py --no-watch'.format(**env))
    local('cd {checkout_path} && ./scripts/coffee.sh --no-watch'.format(**env))

    # minify js
    js_path = '{checkout_path}/static/js/app.js'.format(**env)
    minified_js = local('uglifyjs {}'.format(js_path), capture=True)
    f = open(js_path, 'w')
    f.write(minified_js)
    f.close()


def _fabric_marker(tag):
    """
    Set a resource-version string to use for resource files
    """

    env.resource_version = tag
    local('sed -ire "s/fabric:resource-version/{resource_version}/g" {checkout_path}/config/{config}/localsettings.py'.format(**env))


def _rsync():
    """
    rsync the project from local to remote
    """

    sudo('chown -R {user}:{user} {django_path}'.format(
        user=run('whoami'),
        django_path=env.django_path
    ))

    rsync_project(
        local_dir=env.checkout_path,
        remote_dir=env.deploy_path,
        delete=True
    )

    sudo('ln -s {django_path}/config/{config}/localsettings.py {django_path}/fufufuu/localsettings.py'.format(**env))
    sudo('chown -R www-data:www-data {django_path}'.format(**env))


def _install_requirements():
    """
    install requirements
    """

    with virtualenv():
        with cd('{django_path}'.format(**env)):
            sudo('pip install -r requirements.txt')


def _syncdb_migrate():
    """
    call python manage.py syncb and python manage.py migrate
    """

    with virtualenv():
        with cd('{django_path}'.format(**env)):
            sudo('env')
            sudo('python manage.py syncdb --noinput', user='www-data')
            sudo('python manage.py migrate', user='www-data')
            sudo('python manage.py collectstatic --noinput', user='www-data')


def _install_crontab():
    """
    update the crontab
    """

    sudo('crontab {django_path}/config/{config}/crontab.txt'.format(**env))


#-------------------------------------------------------------------------------

def start():
    """
    starts supervisor (starts fufufuu)
    """

    sudo('supervisord -c {django_path}/config/{config}/supervisord.conf'.format(**env), user='www-data', pty=False)
    sudo('rm -f {static_path}/maintenance.html'.format(**env))


def stop():
    """
    stop supervisor (stops fufufuu)
    """

    sudo('cp {django_path}/static/maintenance.html {static_path}/maintenance.html'.format(**env), user='www-data')
    sudo('killall supervisord', warn_only=True)


def restart():
    """
    convenience method to stop and start the app server
    """

    stop()
    start()


def postgres_reset():
    """
    drops and re-create the database (note: the recreated database has no tables).

    Executed commands:
        drop database if exists fufufuu;
        drop user if exists fufufuu_user;
        create user fufufuu_user with password '<>';
        create database fufufuu;
        grant all privileges on database fufufuu to fufufuu_user;
    """

    if not confirm('Resetting the database, continue?', default=False):
        return

    sudo("echo 'drop database if exists fufufuu;' | sudo -u postgres psql")
    sudo("echo 'drop user if exists fufufuu_user;' | sudo -u postgres psql")

    sudo("echo \"create user fufufuu_user with password \'$FUFUFUU_DB_PASSWORD\';\" | sudo -u postgres psql")
    sudo("echo 'create database fufufuu;' | sudo -u postgres psql")
    sudo("echo 'grant all privileges on database fufufuu to fufufuu_user;' | sudo -u postgres psql")


def postgres_update():
    """
    upload the latest postgres configuration and restart postgres
    """

    sudo('rm -f /etc/postgresql/9.3/main/postgresql.conf')
    put('config/{config}/postgresql.conf'.format(**env), '/etc/postgresql/9.3/main/postgresql.conf', use_sudo=True)
    sudo('/etc/init.d/postgresql restart')


def nginx_update():
    """
    upload the latest nginx configuration and restarts nginx
    """

    sudo('rm -f /etc/nginx/sites-enabled/default')
    sudo('rm -f /etc/nginx/nginx.conf')
    put('config/{config}/nginx.conf'.format(**env), '/etc/nginx/nginx.conf', use_sudo=True)
    sudo('/etc/init.d/nginx restart')


def memcached_update():
    """
    updates the memcached config and restarts memcached
    """

    sudo('rm -fr /etc/memcached.conf')
    put('config/{config}/memcached.conf'.format(**env), '/etc/memcached.conf', use_sudo=True)
    sudo('/etc/init.d/memcached restart')


def exim4_update():
    """
    updates the configuration for exim4 and restarts exim4
    """

    sudo('echo "fufufuu.net" > /etc/mailname')
    sudo('rm -f /etc/exim4/update-exim4.conf.conf')
    put('config/{config}/update-exim4.conf.conf'.format(**env), '/etc/exim4/update-exim4.conf.conf', use_sudo=True)
    sudo('update-exim4.conf')
    append('/etc/email-addresses', 'root: no-reply@fufufuu.net', use_sudo=True)


def manage(command):
    """
    runs 'python manage.py <command>'
    e.g. fab production command:shell --> python manage.py shell
    """

    with virtualenv():
        with cd('{django_path}'.format(**env)):
            sudo('python3.3 manage.py {}'.format(command), user='www-data')


def dump_db():
    """
    generate a SQL dump of the db
    """

    sudo('pg_dump -cO -h localhost -U fufufuu_user fufufuu -p 5432 > dump.sql')
    sudo('rm -f dump.sql.gz')
    sudo('gzip dump.sql')
    get('dump.sql.gz', 'dump.sql.gz')
