from flask import render_template, request, flash, redirect, url_for

from app.entry import entry as ep

@ep.route("/", methods=["GET"])
def hello():
    return "Hello"