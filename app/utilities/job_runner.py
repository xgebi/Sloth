from app.post.scheduled_posts_job import ScheduledPostsJob
from app.rss.rss_job import RssJob


class JobRunner:
    _instance = None

    def __new__(cls, config):
        if cls._instance is None:
            print('Creating the object')
            cls._instance = super(JobRunner, cls).__new__(cls)
            cls.config = config
        return cls._instance

    def init(self, *args, **kwargs):
        pass

    def run(self, *args, **kwargs):
        print("Scheduler runs")
        RssJob(interval=self.config["RSS_JOB_INTERVAL"])
        ScheduledPostsJob(interval=self.config["SCHEDULED_POSTS_INTERVAL"])
