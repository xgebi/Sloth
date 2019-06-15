from flask import render_template, request, flash, redirect, url_for, current_app
import psycopg2
import json

from app.auth import auth

@auth.route("/api/authenticate", methods=["POST", "PUT"])
def authentication():
    
    return json.dumps({"loggedin": False})

def authorization():
    return False