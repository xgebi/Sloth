from flask import render_template, request, flash, redirect, url_for, current_app
import psycopg2
import json

from app.auth import auth

@auth.route("/login", methods=["GET","POST"])
def login():
    if 'sloth_user' in request.cookies:
        return "it's in cookies"
    return render_template("login.html")

def authorization():
    return False