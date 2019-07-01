from flask import current_app
import psycopg2
from psycopg2 import sql
import bcrypt

class User:
    def __init__(self, uuid = None):
        self.uuid = uuid

    def login_user(self, username, password):
        #import pdb; pdb.set_trace() 
        config = current_app.config
        con = psycopg2.connect("dbname='"+config["DATABASE_NAME"]+"' user='"+config["DATABASE_USER"]+"' host='"+config["DATABASE_URL"]+"' password='"+config["DATABASE_PASSWORD"]+"'")
        cur = con.cursor()

        items = []

        try:            
            cur.execute(
                sql.SQL("SELECT password FROM sloth_users WHERE username = '{0}'")
                .format(sql.Identifier(username))
            )
            items = cur.fetchone()
            import pdb; pdb.set_trace() 
        except Exception:
            return False
        
        cur.close()
        con.close()

        items = items[0][1:-1]
        if bcrypt.checkpw(password.encode('utf8'), items.encode('utf8')):
            return True
        return False


    def authorize_user(self):
        pass

    def logout_user(self):
        pass