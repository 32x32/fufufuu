#!/bin/bash

rm fufufuu.sqlite3
rm -fr __pycache__
rm -fr media/*
rm -fr logs/*
python manage.py syncdb --noinput
python manage.py migrate
if [ "$1" != "--empty" ]; then
    python fufufuu/datacreator.py
fi
