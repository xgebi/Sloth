import os
import psycopg


config_filename = os.path.join(os.getcwd(), 'config', f'{os.environ["FLASK_ENV"]}.py')
