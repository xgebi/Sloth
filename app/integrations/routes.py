from flask import request, flash, url_for, current_app, redirect
from app.api.themes import themes as themes
import app
import os
from pathlib import Path
import psycopg2
from psycopg2 import sql
import bcrypt
import json
import requests
from app.post.post_types import PostTypes
from app.authorization.authorize import authorize_rest, authorize_web
from app.utilities.db_connection import db_connection


@themes.route("/settings/integrations", methods=["GET"])
@authorize_web(1)
@db_connection
def show_integrations_settings(*args, connection=None, **kwargs):
    pass


@themes.route("/settings/integrations/larder/connect", methods=["POST"])
@authorize_web(1)
@db_connection
def connect_to_larder_1(*args, connection=None, **kwargs):
    filled = request.form
    if filled.get['client-id'] is None:
        return redirect("/settings/integrations?error")
    return redirect(f"https://larder.io/oauth/authorize/?response_type=code&client_id={filled.get['client-id']}&redirect_uri=http://localhost:5000/settings/integrations/larder/second&scope=read+write")


@themes.route("/settings/integrations/larder/second", methods=["GET"])
@authorize_web(1)
@db_connection
def connect_to_larder_2(*args, connection=None, **kwargs):
    url = 'https://larder.io/oauth/token/'

    response = requests.post(url,
                             {'grant_type': 'authorization_code',
                              'code': code,
                              'client_id': CLIENT_ID,
                              'client_secret': CLIENT_SECRET,
                              'redirect_uri': REDIRECT_URI})