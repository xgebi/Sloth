import psycopg
from flask import request, redirect
import pytz
from pathlib import Path
import os
from app.toes.toes import render_toe_from_path
from app.utilities.db_connection import db_connection
from app.registration.register import Register
from app.toes.hooks import Hooks

from app.registration import registration


@registration.route('/registration', methods=["GET", "POST"])
@db_connection
def registration_steps(*args, connection: psycopg.Connection, **kwargs):
    if Path(os.path.join(os.getcwd(), 'registration.lock')).is_file():
        return redirect("/login")

    if request.method.upper() == "GET":
        return render_toe_from_path(
            path_to_templates=os.path.join(os.getcwd(), 'app', 'templates'),
            template="registration.toe.html",
            data={
                "registration": {},
                "timezones": pytz.all_timezones
            },
            hooks=Hooks()
        )

    if connection is None:
        return render_toe_from_path(
            path_to_templates=os.path.join(os.getcwd(), 'app', 'templates'),
            template="registration.toe.html",
            data={
                "registration": {},
                "timezones": pytz.all_timezones,
                "error": True

            },
            hooks=Hooks()
        ), 500
    # registration
    user_data = request.form.to_dict()

    register = Register(connection)
    result = register.initial_settings(filled=user_data)
    # success
    if result.get("state") is not None and result.get("state") == "ok":
        return redirect("/login")

    # failure
    error = "Unknown error"
    status = result["status"] if result.get("status") else 500

    if result.get("error") is not None:
        error = result["error"]
    return render_toe_from_path(
        path_to_templates=os.path.join(os.getcwd(), 'app', 'templates'),
        template="registration.toe.html",
        data={
            "registration": {},
            "timezones": pytz.all_timezones,
            "error": error
        },
        hooks=Hooks()
    ), status
