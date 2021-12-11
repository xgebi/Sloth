import os
from pathlib import Path
from datetime import datetime
from app.utilities.utilities import parse_raw_post
from app.back_office.post.post_generator import PostGenerator
from app.utilities.db_connection import db_connection

@db_connection
def check_rss_updates():
    pass
