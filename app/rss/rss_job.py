import os
import time
from pathlib import Path
from threading import Thread


class RssJob:
    def __init__(self, interval):
        self.interval = interval
        t = Thread(target=self.run)
        t.start()


    def run(self):
        while not Path(os.path.join(os.getcwd(), 'rss.lock')).is_file():
            print("RssJob ran")
            time.sleep(self.interval)
