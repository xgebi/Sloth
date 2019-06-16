from flask import render_template, request, flash, redirect, url_for, current_app

from app.administration.dashboard import dashboard

@dashboard.route("/dashboard", methods=["GET"])
def dashboard():
    return render_template("dashboard.html")