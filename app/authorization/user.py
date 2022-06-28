import psycopg
from flask import make_response, Response
import bcrypt
from time import time
import json
import uuid
from typing import Tuple, Optional
import re

from app.utilities.db_connection import db_connection, connect_to_db


class UserInfo:
    def __init__(self, user_uuid: str, display_name: str, token: str, expiry_time: float, permissions_level: int):
        self.uuid = user_uuid
        self.display_name = display_name
        self.token = token
        self.expiry_time = expiry_time
        self.permissions_level = permissions_level

    def to_json_string(self) -> str:
        """
        Turns UserInfo object to JSON string

        :return:
        """
        return json.dumps({
            "uuid": self.uuid,
            "displayName": self.display_name,
            "token": self.token,
            "expiryTime": self.expiry_time,
            "permissionsLevel": self.permissions_level,
        })


def test_password(password: str):
    return re.search(r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$ %^&*-]).{8,}$", password)


class User:
    def __init__(self, uuid: Optional[str] = None, token: Optional[str] = None):
        self.uuid = uuid
        self.token = token

    def login_user(self, username: str, password: str) -> Optional[UserInfo]:
        """
        Authenticates user in if the user exists, returns None if user doesn't exists or is not authenticated

        :param username:
        :param password:
        :return:
        """
        with connect_to_db() as connection:
            with connection.cursor(row_factory=psycopg.rows.dict_row) as cur:
                try:
                    cur.execute(
                        """SELECT uuid, password, display_name, permissions_level 
                        FROM sloth_users WHERE username = %s""",
                        (username, )
                    )
                    items = cur.fetchone()
                except psycopg.errors.DatabaseError:
                    return None

                if items is None:
                    return None

                if bcrypt.checkpw(password.encode('utf8'), items["password"].encode('utf8')):
                    token = str(uuid.uuid4())
                    expiry_time = time() + 1800  # 30 minutes

                    try:
                        cur.execute(
                            """UPDATE sloth_users SET token = %s, expiry_date = %s WHERE uuid = %s""",
                            (token, expiry_time, items["uuid"])
                        )
                        connection.commit()
                    except psycopg.errors.DatabaseError:
                        return None

                    return UserInfo(
                        user_uuid=items["uuid"],
                        display_name=items["display_name"],
                        token=token,
                        expiry_time=expiry_time * 1000,
                        permissions_level=items["permissions_level"]
                    )
                return None

    def authorize_user(self, *args, permissions_level: int, **kwargs) -> Tuple[bool, int]:
        """
        Checks if user is authorized to access and/or update data

        :param permissions_level:
        :return:
        """
        with connect_to_db() as connection:
            with connection.cursor(row_factory=psycopg.rows.dict_row) as cur:
                try:
                    cur.execute(
                        """SELECT permissions_level, expiry_date, token FROM sloth_users WHERE uuid = %s""",
                        (self.uuid, )
                    )
                    items = cur.fetchone()
                except psycopg.errors.DatabaseError:
                    return False, -1

                if items is None or permissions_level > items['permissions_level'] or time() > items['expiry_date'] or self.token != items['token']:
                    return False, -1

                try:
                    cur.execute(
                        """UPDATE sloth_users SET expiry_date = %s WHERE uuid = %s""",
                        (time() + 1800, self.uuid)
                    )
                    connection.commit()
                except psycopg.errors.DatabaseError:
                    return False, -1

            return True, int(items['permissions_level'])

    @db_connection
    def logout_user(self, connection: psycopg.Connection):
        """
        Logs out user

        :param connection:
        :return:
        """
        with connection.cursor() as cur:
            try:
                cur.execute(
                    """UPDATE sloth_users SET expiry_date = %s, token = %s WHERE uuid = %s""",
                    (0, "", self.uuid)
                )
                connection.commit()
            except psycopg.errors.DatabaseError:
                return

    def refresh_login(self) -> Tuple[Response, int]:
        """
        Refreshes credentials for logged in user

        :return:
        """
        with connect_to_db() as connection:
            with connection.cursor(row_factory=psycopg.rows.dict_row) as cur:
                try:
                    cur.execute(
                        """SELECT token, expiry_date FROM sloth_users WHERE uuid = %s""",
                        (self.uuid, )
                    )

                    item = cur.fetchone()
                    if time() > item['expiry_date']:
                        response = make_response(json.dumps({"error": "Authorization timeout"}))
                        response.headers['Content-Type'] = 'application/json'
                        code = 403

                        return response, code

                    if item['token'] != self.token:
                        response = make_response(json.dumps({"Unauthorized": True}))
                        response.headers['Content-Type'] = 'application/json'
                        code = 403

                        return response, code

                    expiry_time = time() + 1800  # 30 minutes

                    cur.execute(
                        """UPDATE sloth_users SET expiry_date = %s WHERE uuid = %s""",
                        (expiry_time, self.uuid)
                    )
                    connection.commit()
                except psycopg.errors.DatabaseError:
                    response = make_response(json.dumps({"error": "Could not refresh login"}))
                    response.headers['Content-Type'] = 'application/json'
                    code = 500

                    return response, code

            response = make_response(json.dumps({"refreshLogin": True}))
            response.headers['Content-Type'] = 'application/json'
            code = 200

            return response, code

