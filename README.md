Fufufuu
=======

Welcome to Fufufuu version 3 repository.

Development Environment Setup
-----------------------------

Developing for Fufufuu version 3 on OS X requires:

* Xcode with GCC compiler installed
* [brew](http://brew.sh/)
* [npm](https://npmjs.org/)

Install the following brew packages

    > brew update
    > brew install libjpeg libpng postgresql python3

Install the following npm packages

    > sudo npm install -g coffee-script less markdown

Start by installing `pip`

    > sudo easy_install pip
    > sudo pip install virtualenv virtualenvwrapper
    > mkdir ~/.envs

Add the following lines to `.bash_profile`

    export WORKON_HOME=~/.envs
    source /usr/local/bin/virtualenvwrapper.sh

Restart your terminal, then create a new virtual environment. Check that the installed version are correct.

    > mkvirtualenv --python=python3.3 fufufuu
    (fufufuu) > python --version
    Python 3.3.3
    (fufufuu) > pip --version
    pip 1.5.1 from ... (python 3.3)

The `(fufufuu)` prefix indicates the `fufufuu` virtual environment is active. To work a virtual environment

    > workon fufufuu
    (fufufuu) >

Install the required python packages

    (fufufuu) > pip install -r requirements.txt

There are two scripts that need to be run in the background:

    (fufufuu) > ./scripts/less.py         # compile less files
    (fufufuu) > ./scripts/coffee.sh       # compile coffee scripts
