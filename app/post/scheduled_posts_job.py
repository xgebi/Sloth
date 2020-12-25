import os
import time
from pathlib import Path
from threading import Thread


class ScheduledPostsJob:
    def __init__(self, interval):
        self.interval = interval
        t = Thread(target=self.run)
        t.start()

    def run(self):
        print("ScheduledPostsJob started")
        while not Path(os.path.join(os.getcwd(), 'schedule.lock')).is_file():
            if not Path(os.path.join(os.getcwd(), 'generating.lock')).is_file():
                print("ScheduledPostsJob ran")
            time.sleep(self.interval)
