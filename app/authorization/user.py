from flask import current_app, make_response, Response
import psycopg2
from psycopg2 import sql
import bcrypt
from time import time
import json
import uuid
from typing import Tuple

from app.utilities.db_connection import db_connection_legacy


class UserInfo:
    def __init__(self, user_uuid: str, display_name: str, token: str, expiry_time: float, permissions_level: int):
        self.uuid = user_uuid
        self.display_name = display_name
        self.token = token
        self.expiry_time = expiry_time
        self.permissions_level = permissions_level

    def to_json_string(self) -> str:
        return json.dumps({
            "uuid": self.uuid,
            "displayName": self.display_name,
            "token": self.token,
            "expiryTime": self.expiry_time,
            "permissionsLevel": self.permissions_level,
        })


class User:
    def __init__(self, uuid=None, token=None):
        self.uuid = uuid
        self.token = token

    @db_connection_legacy
    def login_user(self, username: str, password: str, connection=None) -> UserInfo or None:
        config = current_app.config
        if connection is None:
            return None
        cur = connection.cursor()

        items = []

        try:
            cur.execute(
                sql.SQL("SELECT uuid, password, display_name, permissions_level FROM sloth_users WHERE username = %s"),
                [username]
            )
            items = cur.fetchone()
        except Exception as e:
            return None

        if items is None:
            return None

        trimmed_items = {
            "uuid": items[0],
            "password": items[1],
            "display_name": items[2],
            "permissions_level": items[3]
        }

        if bcrypt.checkpw(password.encode('utf8'), trimmed_items["password"].encode('utf8')):
            token = str(uuid.uuid4())
            expiry_time = time() + 1800  # 30 minutes

            try:
                cur.execute(
                    sql.SQL("UPDATE sloth_users SET token = %s, expiry_date = %s WHERE uuid = %s"),
                    (token, expiry_time, trimmed_items["uuid"])
                )
                connection.commit()
            except Exception as e:
                cur.close()
                connection.close()
                return None

            cur.close()
            connection.close()
            return UserInfo(
                user_uuid=trimmed_items["uuid"],
                display_name=trimmed_items["display_name"],
                token=token,
                expiry_time=expiry_time * 1000,
                permissions_level=trimmed_items["permissions_level"]
            )

        cur.close()
        connection.close()

        return None

    def authorize_user(self, permissions_level) -> Tuple[bool, int]:
        config = current_app.config
        con = psycopg2.connect(dbname=config["DATABASE_NAME"], user=config["DATABASE_USER"],
                               host=config["DATABASE_URL"], port=config["DATABASE_PORT"],
                               password=config["DATABASE_PASSWORD"])
        cur = con.cursor()

        try:
            cur.execute(
                sql.SQL("SELECT permissions_level, expiry_date, token FROM sloth_users WHERE uuid = %s"), [self.uuid]
            )
            items = cur.fetchone()
        except Exception as e:
            cur.close()
            con.close()
            return False, -1

        if items is None or permissions_level > items[0] or time() > items[1] or self.token != items[2]:
            cur.close()
            con.close()
            return False, -1

        try:
            cur.execute(
                sql.SQL("UPDATE sloth_users SET expiry_date = %s WHERE uuid = %s"),
                (time() + 1800, self.uuid)
            )
            con.commit()
        except Exception as e:
            cur.close()
            con.close()
            return False, -1

        cur.close()
        con.close()
        return True, int(items[0])

    def logout_user(self):
        config = current_app.config
        con = psycopg2.connect(dbname=config["DATABASE_NAME"], user=config["DATABASE_USER"],
                               host=config["DATABASE_URL"], port=config["DATABASE_PORT"],
                               password=config["DATABASE_PASSWORD"])
        cur = con.cursor()

        try:
            cur.execute(
                sql.SQL("UPDATE sloth_users SET expiry_date = %s, token = %s WHERE uuid = %s"), (0, "", self.uuid)
            )
            con.commit()
        except Exception as e:
            cur.close()
            con.close()
            return
        cur.close()
        con.close()

    def refresh_login(self) -> Tuple[Response, int]:
        config = current_app.config
        con = psycopg2.connect(dbname=config["DATABASE_NAME"], user=config["DATABASE_USER"],
                               host=config["DATABASE_URL"], port=config["DATABASE_PORT"],
                               password=config["DATABASE_PASSWORD"])
        cur = con.cursor()

        try:
            cur.execute(
                sql.SQL("SELECT token, expiry_date FROM sloth_users WHERE uuid = %s"), [self.uuid]
            )

            item = cur.fetchone()
            if item[1] < time():
                response = make_response(json.dumps({"error": "Authorization timeout"}))
                response.headers['Content-Type'] = 'application/json'
                code = 403

                return response, code

            if item[0] != self.token:
                response = make_response(json.dumps({"Unauthorized": True}))
                response.headers['Content-Type'] = 'application/json'
                code = 403

                return response, code

            expiry_time = time() + 1800  # 30 minutes

            cur.execute(
                sql.SQL("UPDATE sloth_users SET expiry_date = %s WHERE uuid = %s"), (expiry_time, self.uuid)
            )
            con.commit()
        except Exception as e:
            cur.close()
            con.close()

            response = make_response(json.dumps({"Unauthorized": True}))
            response.headers['Content-Type'] = 'application/json'
            code = 403

            return response, code

        cur.close()
        con.close()

        response = make_response(json.dumps({"refreshLogin": True}))
        response.headers['Content-Type'] = 'application/json'
        code = 200

        return response, code
