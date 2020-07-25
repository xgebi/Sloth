from app.scheduler.scheduler import Scheduler
from app.scheduler.GenerationQueueJob import GenerationQueueJob


class ScheduledJobs:
    scheduler = {}

    def __init__(self):
        self.scheduler = Scheduler()
        self.scheduler.register_job(job=GenerationQueueJob(interval=1))
