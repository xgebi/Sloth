import os
import time
from pathlib import Path
from threading import Thread


def scheduled_posts_job():
    if not Path(os.path.join(os.getcwd(), 'generating.lock')).is_file():
        print("ScheduledPostsJob ran")
