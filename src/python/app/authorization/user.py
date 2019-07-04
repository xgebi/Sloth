from flask import current_app
import psycopg2
from psycopg2 import sql
import bcrypt
from time import time
import random
import uuid

class User:
    def __init__(self, uuid = None, token = None):
        self.uuid = uuid
        self.token = token

    def login_user(self, username, password):
        config = current_app.config
        con = psycopg2.connect("dbname='"+config["DATABASE_NAME"]+"' user='"+config["DATABASE_USER"]+"' host='"+config["DATABASE_URL"]+"' password='"+config["DATABASE_PASSWORD"]+"'")
        cur = con.cursor()

        items = []

        try:            
            cur.execute(
                sql.SQL("SELECT uuid, password FROM sloth_users WHERE username = %s"),
                [username]
            )
            items = cur.fetchone()
        except Exception:
            return None
        
        trimmed_items = (items[0], items[1])
        token = ""
        
        if bcrypt.checkpw(password.encode('utf8'), trimmed_items[1].encode('utf8')):
            token = str(uuid.uuid4())
            expiry_time = time() + 1800 # 30 minutes

            try:            
                cur.execute(
                    sql.SQL("UPDATE sloth_users SET token = %s, expiry_date = %s WHERE uuid = %s"), (token, expiry_time, trimmed_items[0])
                )
                con.commit()
            except Exception:
                cur.close()
                con.close()
                return None
            
            cur.close()
            con.close()
            return (trimmed_items[0], token)
        
        cur.close()
        con.close()

        return None


    def authorize_user(self, permissions_level):
        config = current_app.config
        con = psycopg2.connect("dbname='"+config["DATABASE_NAME"]+"' user='"+config["DATABASE_USER"]+"' host='"+config["DATABASE_URL"]+"' password='"+config["DATABASE_PASSWORD"]+"'")
        cur = con.cursor()
        
        try:            
            cur.execute(
                sql.SQL("SELECT permissions_level, expiry_date, token FROM sloth_users WHERE uuid = %s"), [self.uuid]
            )
            items = cur.fetchone()
        except Exception:
            cur.close()
            con.close()            
            return False
        
        if (permissions_level > items[0]):
            cur.close()
            con.close()
            return False

        if (time() > items[1]):
            cur.close()
            con.close()
            return False

        if (self.token != items[2]):
            cur.close()
            con.close()
            return False
        
        try:            
            cur.execute(
                sql.SQL("UPDATE sloth_users SET expiry_date = %s WHERE uuid = %s"),
                (time() + 1800, self.uuid)
            )
            con.commit()
        except Exception:
            cur.close()
            con.close()
            return False

        cur.close()
        con.close()
        return True

    def logout_user(self):
        pass