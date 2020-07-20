from flask import request, flash, url_for, current_app
from app.api.themes import themes as themes
import app
import os
from pathlib import Path
import psycopg2
from psycopg2 import sql
import bcrypt
import json
from app.posts.post_types import PostTypes
from app.authorization.authorize import authorize_rest, authorize_web
from app.utilities.db_connection import db_connection


@themes.route("/settings/language", methods=["GET"])
@authorize_web(1)
@db_connection
def show_language_settings(*args, connection=None, **kwargs):
    pass


@themes.route("/settings/language/<lang_id>", methods=["GET"])
@authorize_web(1)
@db_connection
def show_language_info(*args, connection=None, lang_id, **kwargs):
    pass


@themes.route("/settings/language", methods=["POST", "PUT"])
@authorize_web(1)
@db_connection
def save_language_info(*args, connection=None, **kwargs):
    pass

