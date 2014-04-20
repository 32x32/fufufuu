#!/bin/sh

rm fufufuu.sqlite3
rm -fr __pycache__
rm -fr media/*
rm -fr logs/*
python manage.py syncdb --noinput

python manage.py schemamigration account --auto --update
python manage.py schemamigration blog --auto --update
python manage.py schemamigration comment --auto --update
python manage.py schemamigration core --auto --update
python manage.py schemamigration dmca --auto --update
python manage.py schemamigration download --auto --update
python manage.py schemamigration image --auto --update
python manage.py schemamigration legacy --auto --update
python manage.py schemamigration manga --auto --update
python manage.py schemamigration report --auto --update
python manage.py schemamigration tag --auto --update
