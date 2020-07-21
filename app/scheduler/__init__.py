from app.scheduler.scheduler import Scheduler


class ScheduledJobs:

    def __init__(self):
        post_scheduler = Scheduler(interval=60, function=self.check_posts)

    def check_posts(self, *args, **kwargs):
        pass
