#!/bin/sh

rm fufufuu.sqlite3
rm -fr __pycache__
rm -fr media/*
rm -fr logs/*
python manage.py syncdb --noinput

python manage.py schemamigration account --initial --update
python manage.py schemamigration blog --initial --update
python manage.py schemamigration comment --initial --update
python manage.py schemamigration core --initial --update
python manage.py schemamigration download --initial --update
python manage.py schemamigration image --initial --update
python manage.py schemamigration legacy --initial --update
python manage.py schemamigration manga --initial --update
python manage.py schemamigration report --initial --update
python manage.py schemamigration tag --initial --update
