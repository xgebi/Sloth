from flask import render_template, request, flash, redirect, url_for, current_app, abort
import psycopg2
import os
import json

from app.administration.themes import themes
from app.authorization.user import User
from app.administration.posts.post_types import PostTypes

# TODO add list of themes page
@themes.route("/themes")
def redirect_to_list():
	return redirect("/themes/list")

@themes.route("/themes/list")
def show_theme_list():
	userId = request.cookies.get('userID')
	userToken = request.cookies.get('userToken')
	user = User(userId, userToken)
	if user.authorize_user(0):
		config = current_app.config
		con = psycopg2.connect("dbname='"+config["DATABASE_NAME"]+"' user='"+config["DATABASE_USER"]+"' host='"+config["DATABASE_URL"]+"' password='"+config["DATABASE_PASSWORD"]+"'")
		cur = con.cursor()
		post_types = PostTypes.get_post_type_list(None, con)


		cur.close()
		con.close()
	
		theme_folders = os.listdir(config["THEMES_PATH"])
		valid_themes = [theme for theme in theme_folders if os.path.isfile(os.path.join(config["THEMES_PATH"], theme, "theme.json"))]

		themes_data = []
		for theme in valid_themes:
			with open(os.path.join(config["THEMES_PATH"], theme, "theme.json")) as f:
				themes_data.append(json.load(f))

		return render_template('themes_list.html', themes = themes_data)
	return redirect("/login")

# TODO select theme and generate content
@themes.route("/themes/use/<name>")
def use_theme(name):
	userId = request.cookies.get('userID')
	userToken = request.cookies.get('userToken')
	user = User(userId, userToken)
	if user.authorize_user(0):
		config = current_app.config
		con = psycopg2.connect("dbname='"+config["DATABASE_NAME"]+"' user='"+config["DATABASE_USER"]+"' host='"+config["DATABASE_URL"]+"' password='"+config["DATABASE_PASSWORD"]+"'")
		cur = con.cursor()
		post_types = PostTypes.get_post_type_list(None, con)

		try:
			cur.execute("UPDATE sloth_settings SET settings_value = %s", name)
			con.commit()
		except expression as identifier:
			abort(500)
		cur.close()
		con.close()
		# TODO regenerate files

	return redirect("/login")

@themes.route("/themes/settings")
def display_theme_settings():
	userId = request.cookies.get('userID')
	userToken = request.cookies.get('userToken')
	user = User(userId, userToken)
	if user.authorize_user(0):
		config = current_app.config
		con = psycopg2.connect("dbname='"+config["DATABASE_NAME"]+"' user='"+config["DATABASE_USER"]+"' host='"+config["DATABASE_URL"]+"' password='"+config["DATABASE_PASSWORD"]+"'")
		cur = con.cursor()
		post_types = PostTypes.get_post_type_list(None, con)

		raw_items = []
		theme_name = ""
		try:
			cur.execute("SELECT settings_value FROM sloth_settings WHERE settings_name = 'active_theme'")
			theme_name = cur.fetchone()		
			cur.execute("SELECT settings_name, display_name, settings_value FROM sloth_settings WHERE section_name = %s", theme_name)
			raw_items = cur.fetchall()
		except expression as identifier:
			abort(500)
		cur.close()
		con.close()

		items = {setting[0]: setting for setting in raw_items}
		
		return render_template("theme_settings.html", theme_name = theme_name[0], options = items, post_types = post_types)
	return redirect("/login")



@themes.route("/themes/settings/save", methods = ['POST'])
def save_theme_settings():
	userId = request.cookies.get('userID')
	userToken = request.cookies.get('userToken')
	user = User(userId, userToken)
	if user.authorize_user(0):
		config = current_app.config
		con = psycopg2.connect("dbname='"+config["DATABASE_NAME"]+"' user='"+config["DATABASE_USER"]+"' host='"+config["DATABASE_URL"]+"' password='"+config["DATABASE_PASSWORD"]+"'")
		cur = con.cursor()
		post_types = PostTypes.get_post_type_list(None, con)

		try:
			con.rollback()
			for option in request.form:
				cur.execute("UPDATE sloth_settings SET settings_value = %s WHERE settings_name = %s", (request.form.get(option), option))				
			con.commit()
		except Exception as e:
			print(e)
			abort(500)
		
		# TODO regenerate files
		cur.close()
		con.close()
		return redirect("/themes/settings")
	return redirect("/login")