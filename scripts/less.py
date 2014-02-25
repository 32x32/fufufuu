#!/usr/bin/env python3

import datetime
import os
import re
import subprocess
import time
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from watchdog.observers import Observer

#-------------------------------------------------------------------------------
# less.py configuration
#-------------------------------------------------------------------------------

PATTERN = re.compile('.*\.less$')

PATH = 'static/css'

FILES = [
    ('app.less', 'app.css'),
]

#-------------------------------------------------------------------------------


class EventHandler(FileSystemEventHandler):

    def dispatch(self, event):
        if event.is_directory or not PATTERN.match(event.src_path):
            return

        for input_path, output_path in FILES:
            input_path = os.path.join(PATH, input_path)
            output = open(os.path.join(PATH, output_path), 'wb')

            subprocess.call(['lessc', '-x', input_path], stdout=output)

            now = datetime.datetime.now().strftime('%H:%M:%S')
            print('{} - compiled {}'.format(now, output_path))


if __name__ == '__main__':
    EventHandler().dispatch(FileSystemEvent('initial compile', 'static/css-jinja/app.less'))

    observer = Observer()
    observer.schedule(EventHandler(), path=PATH, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
