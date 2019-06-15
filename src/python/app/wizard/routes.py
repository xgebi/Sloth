from flask import render_template, request, flash, redirect, url_for, current_app
import psycopg2

from app.wizard import wizard as wiz

@wiz.route("/register", methods=["GET", "POST"])
def wizard():
    filled = { "username": "Sarah" }
    return render_template("initial_step.html", filled=filled)

@wiz.route("/process-registration", methods=["POST"])
def registration_processing():
    return ""

@wiz.route("/registered", methods=["GET"])
def registered():
    return ""