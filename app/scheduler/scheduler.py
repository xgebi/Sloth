from threading import Timer


class Scheduler:
    jobs = []
    base_interval = 60000

    def __init__(self, *args, **kwargs):
        self._timer = None
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.start()

    def register_job(self, *args, job, **kwargs):
        self.jobs.append(job)

    def check_jobs(self):
        self.is_running = False
        self.start()
        for job in self.jobs:
            job.run()

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.base_interval, self.check_jobs)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False
