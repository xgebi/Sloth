from flask import request, redirect, make_response
from functools import wraps
import json

from app.authorization.user import User


def authorize_rest(permission_level: int):
    """
    Decorator that checks one has privileges to access REST API

    :param permission_level:
    :return:
    """
    def inner(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            auth = request.headers.get('authorization').split(":")
            user = User(auth[1], auth[2])

            pass_token = user.authorize_user(permissions_level=permission_level)

            if pass_token:
                return fn(*args, permission_level=pass_token[1], **kwargs)

            response = make_response(json.dumps({"Unauthorized": True}))
            response.headers['Content-Type'] = 'application/json'
            code = 403

            return response, code

        return wrapper

    return inner


def authorize_web(permission_level: int):
    """
    Decorator that checks one has privileges to access a page

    :param permission_level:
    :return:
    """
    def inner(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            auth = request.cookies.get('sloth_session')
            if auth is None:
                return redirect("/login" if request.path == "/login" else f"/login?redirect={request.path}")
            auth = auth.split(":")
            if len(auth) != 3:
                return redirect("/login" if request.path == "/login" else f"/login?redirect={request.path}")
            user = User(auth[1], auth[2])
            pass_token = user.authorize_user(permissions_level=permission_level)

            if not pass_token:
                return redirect("/login" if request.path == "/login" else f"/login?redirect={request.path}")

            if pass_token[0]:
                user.refresh_login()
                return fn(*args, permission_level=pass_token[1], **kwargs)
            return redirect("/login" if request.path == "/login" else f"/login?redirect={request.path}")

        return wrapper

    return inner
