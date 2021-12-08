from datetime import datetime
import time


def publish_posts():
    while True:
        print(f"Scheduled at {datetime.now()}")
        time.sleep(60)


def post_to_twitter():
    while True:
        print(f"Scheduled at {datetime.now()}")
        time.sleep(60)