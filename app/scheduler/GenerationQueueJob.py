import psycopg
import psycopg2
from psycopg2 import sql, errors
from datetime import datetime
from app.post.post_generator import PostGenerator
from app.utilities.db_connection import db_connection


from app.scheduler.Job import Job


class GenerationQueueJob(Job):

    def __init__(self, *args, interval: int, **kwargs):
        self.interval = interval
        self.next_run = datetime.now() + (interval * 60)

    @db_connection
    def run(self, *args, connection: psycopg.Connection, **kwargs):
        self.last_run = datetime.now()
        self.running = True

        try:
            with connection.cursor() as cur:
                cur.execute("""SELECT all_posts, post_uuid FROM sloth_generation_queue ORDER BY timedate_added ASC;""")
        except Exception as e:
            print(e)
        connection.close()
        self.next_run = datetime.now() + (self.interval * 60)
        self.running = False

    @db_connection
    def add_to_queue(self, *args, post, connection: psycopg.Connection, **kwargs):
        # sloth_generation_queue
        pass
