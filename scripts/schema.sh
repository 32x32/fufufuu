#!/bin/sh

python manage.py schemamigration account --initial --update
python manage.py schemamigration comment --initial --update
python manage.py schemamigration core --initial --update
python manage.py schemamigration download --initial --update
python manage.py schemamigration image --initial --update
python manage.py schemamigration legacy --initial --update
python manage.py schemamigration manga --initial --update
python manage.py schemamigration report --initial --update
python manage.py schemamigration tag --initial --update
