import psycopg
from flask import request, current_app, abort, redirect, render_template
from psycopg2 import sql

from app.utilities.db_connection import db_connection
from app.authorization.authorize import authorize_web

from app.post.post_types import PostTypes

from app.settings.users import settings_users


@settings_users.route("/settings/users")
@authorize_web(1)
@db_connection
def show_users_list(*args, permission_level: int, connection: psycopg.Connection, **kwargs):
    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)

    raw_users = []
    try:
        with connection.cursor() as cur:
            cur.execute(
                "SELECT uuid, username, display_name FROM sloth_users"
            )
            raw_users = cur.fetchall()
    except Exception as e:
        print("db error")
        connection.close()
        abort(500)

    connection.close()

    user_list = []
    for user in raw_users:
        user_list.append({
            "uuid": user[0],
            "username": user[1],
            "display_name": user[2]
        })

    return render_template("users-list.html", post_types=post_types_result, permission_level=permission_level,
                           user_list=user_list)


@settings_users.route("/settings/users/<user>")
@authorize_web(0)
@db_connection
def show_user(*args, permission_level: int, connection: psycopg.Connection, user: str, **kwargs):
    token = request.cookies.get('sloth_session').split(":")

    if permission_level == 0 and token[1] != user:
        return redirect("/unauthorized")

    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)

    try:
        with connection.cursor() as cur:
            cur.execute(
                "SELECT uuid, username, display_name, email, permissions_level FROM sloth_users WHERE uuid = %s",
                (token[1],))
            raw_user = cur.fetchone()
    except Exception as e:
        print("db error")
        connection.close()
        abort(500)

    connection.close()

    user = {
        "uuid": raw_user[0],
        "username": raw_user[1],
        "display_name": raw_user[2],
        "email": raw_user[3],
        "permissions_level": raw_user[4]
    }

    return render_template("user.html", post_types=post_types_result, permission_level=permission_level, user=user)


@settings_users.route("/settings/my-account")
@authorize_web(0)
@db_connection
def show_my_account(*args, permission_level: int, connection: psycopg.Connection, **kwargs):
    token = request.cookies.get('sloth_session').split(":")

    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)

    try:
        with connection.cursor() as cur:
            cur.execute(
                "SELECT uuid, username, display_name, email, permissions_level FROM sloth_users WHERE uuid = %s",
                (token[1],))
            raw_user = cur.fetchone()
    except Exception as e:
        print("db error")
        connection.close()
        abort(500)

    connection.close()

    user = {
        "uuid": raw_user[0],
        "username": raw_user[1],
        "display_name": raw_user[2],
        "email": raw_user[3],
        "permissions_level": raw_user[4]
    }

    return render_template("user.html", post_types=post_types_result, permission_level=permission_level, user=user)


@settings_users.route("/settings/users/<user>/save", methods=["POST"])
@authorize_web(0)
@db_connection
def save_user(*args, permission_level: int, connection: psycopg.Connection, user: str, **kwargs):
    token = request.cookies.get('sloth_session').split(":")
    filled = request.form

    if permission_level == 0 and token[1] != user:
        return redirect("/unauthorized")

    try:
        with connection.cursor() as cur:
            # TODO detect display_name change
            cur.execute("UPDATE sloth_users SET display_name = %s, email = %s, permissions_level = %s WHERE uuid = %s",
                        (filled.get("display_name"), filled.get("email"), int(filled.get("permissions")), user))
            connection.commit()
    except Exception as e:
        print("db error")
        abort(500)

    connection.close()

    if token[1] == user:
        return redirect("/settings/my-account")
    return redirect(f"/settings/users/{user}")

# TODO change password
