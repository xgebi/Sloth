from flask import request, flash, url_for, current_app
import app
import os
from pathlib import Path
import psycopg2
from psycopg2 import sql
import bcrypt
import json
from app.post.post_types import PostTypes
from app.authorization.authorize import authorize_rest, authorize_web
from app.utilities.db_connection import db_connection

from app.settings.language_settings import language_settings


@language_settings.route("/settings/language", methods=["GET"])
@authorize_web(1)
@db_connection
def show_language_settings(*args, connection=None, **kwargs):
    pass


@language_settings.route("/settings/language/<lang_id>", methods=["GET"])
@authorize_web(1)
@db_connection
def show_language_info(*args, connection=None, lang_id, **kwargs):
    pass


@language_settings.route("/settings/language", methods=["POST", "PUT"])
@authorize_web(1)
@db_connection
def save_language_info(*args, connection=None, **kwargs):
    pass


@language_settings.route("/settings/language/delete", methods=["DELETE"])
@authorize_web(1)
@db_connection
def delete_language(*args, connection=None, **kwargs):
    pass

