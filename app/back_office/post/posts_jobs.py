import os
from pathlib import Path
from datetime import datetime

import psycopg

from app.back_office.post.post_generator import PostGenerator
from app.utilities.db_connection import db_connection

# TODO refactor this completely
@db_connection
def scheduled_posts_job(*args, connection, **kwargs):
    if Path(os.path.join(os.getcwd(), 'schedule.lock')).is_file():
        return
    with open(os.path.join(os.getcwd(), 'schedule.lock'), 'w') as f:
        f.write("")

    if not Path(os.path.join(os.getcwd(), 'generating.lock')).is_file():
        try:
            with connection.cursor(row_factory=psycopg.rows.dict_row) as cur:
                cur.execute("""
                        SELECT sp.uuid, sp.original_lang_entry_uuid, sp.lang, sp.slug, sp.post_type, sp.author, sp.title,
                                sp.css, sp.use_theme_css, sp.js, sp.use_theme_js, sp.thumbnail, sp.publish_date, 
                                sp.update_date, sp.post_status, sp.imported, sp.import_approved, sp.meta_description, 
                                sp.twitter_description, spf.uuid, spf.slug, spf.display_name
                                FROM sloth_posts as sp 
                                INNER JOIN sloth_post_formats spf on spf.uuid = sp.post_format
                                WHERE sp.post_status = 'scheduled' AND sp.publish_date < %s;""",
                            (datetime.now().timestamp() * 1000,))
                raw_posts = cur.fetchall()
                libraries = {}
                for post in raw_posts:
                    cur.execute("""SELECT sl.location, spl.hook_name
                            FROM sloth_post_libraries AS spl
                            INNER JOIN sloth_libraries sl on sl.uuid = spl.library
                            WHERE spl.post = %s;""",
                                (post['uuid'],))
                    libraries[post['uuid']] = cur.fetchall()

                    cur.execute("""UPDATE sloth_posts SET post_status = 'published' WHERE uuid = %s;""",
                                (post['uuid'],))
                connection.commit()
        except Exception as e:
            connection.close()
            return

        os.remove(Path(os.path.join(os.getcwd(), 'schedule.lock')))
        gen = PostGenerator(connection=connection)
        for raw_post in raw_posts:
            post = {} #parse_raw_post(raw_post)
            post['post_status'] = "published"
            post["libraries"] = libraries[post["uuid"]]
            gen.run(post=post, multiple=True)
