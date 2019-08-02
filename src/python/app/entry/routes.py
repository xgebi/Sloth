from flask import render_template, request, flash, redirect, url_for, current_app
import psycopg2
from psycopg2 import sql
import time

from app.entry import entry as ep

@ep.route("/", methods=["GET"])
def entry_point():
	return render_template("index.html")