#!/bin/sh

python manage.py schemamigration account --initial --update
python manage.py schemamigration manga --initial --update
