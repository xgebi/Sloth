import os
from pathlib import Path
from psycopg2 import sql, connect
from datetime import datetime
from app.utilities import parse_raw_post
from app.post.post_generator import PostGenerator
from app.utilities.db_connection import db_connection

@db_connection
def check_rss_updates():
    pass
