from flask import request, flash, url_for, current_app, redirect
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
from app.utilities.db_connection import db_connection_legacy
from app.integrations import integrations

@integrations.route("/settings/integrations", methods=["GET"])
@authorize_web(1)
@db_connection_legacy
def show_integrations_settings(*args, connection=None, **kwargs):
    pass
