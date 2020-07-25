from datetime import datetime

class Job:
    last_run = -1
    next_run = -1
    interval = 0
    running = False

    def __init__(self, *args, interval, **kwargs):
        self.interval = interval
        self.next_run = datetime.now() + (interval * 60)

    def run(self, *args, **kwargs):
        self.last_run = datetime.now()
        self.running = True

        self.next_run = datetime.now() + (self.interval * 60)
        self.running = False
