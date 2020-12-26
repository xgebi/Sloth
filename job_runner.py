import os
import psycopg2

from app.rss.rss_job import RssJob

config_filename = os.path.join(os.getcwd(), 'config', f'{os.environ["FLASK_ENV"]}.py')
