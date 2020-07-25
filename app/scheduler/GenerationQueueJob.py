import psycopg2
from psycopg2 import sql, errors
from datetime import datetime
from app.post.posts_generator import PostsGenerator
from app.utilities.db_connection import db_connection


from app.scheduler.Job import Job


class GenerationQueueJob(Job):

    def __init__(self, *args, interval, **kwargs):
        self.interval = interval
        self.next_run = datetime.now() + (interval * 60)

    @db_connection
    def run(self, *args, connection, **kwargs):
        self.last_run = datetime.now()
        self.running = True

        cur = connection.cursor()
        try:
            cur.execute(
                sql.SQL("""SELECT all_posts, post_uuid FROM sloth_generation_queue ORDER BY timedate_added ASC;""")
            )
        except Exception as e:
            print(e)

        self.next_run = datetime.now() + (self.interval * 60)
        self.running = False

    @db_connection
    def add_to_queue(self, *args, post, connection, **kwargs):
        # sloth_generation_queue
        pass
