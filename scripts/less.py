#!/usr/bin/env python3

import datetime
import os
import re
import subprocess
import time
from watchdog.events import FileSystemEventHandler
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
# event handler class
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
            file_path = event.src_path[event.src_path.rindex(PATH):]
            print('{} - {} - {}'.format(now, event.event_type, file_path))
            print('{} - compiled {}'.format(now, output_path))


if __name__ == '__main__':
    observer = Observer()
    observer.schedule(EventHandler(), path=PATH, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
