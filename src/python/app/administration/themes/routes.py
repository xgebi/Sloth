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

		return render_template('themes_list.html', themes = themes_data, post_types = post_types)
	return redirect("/dashboard")

# TODO select theme and generate content
@themes.route("/themes/use/<name>")
def use_theme(name):
	config = current_app.config
	con = psycopg2.connect("dbname='"+config["DATABASE_NAME"]+"' user='"+config["DATABASE_USER"]+"' host='"+config["DATABASE_URL"]+"' password='"+config["DATABASE_PASSWORD"]+"'")
	cur = con.cursor()
	post_types = PostTypes.get_post_type_list(None, con)

	# TODO update active theme indicator in database
	cur.close()
	con.close()
	# TODO regenerate files

@themes.route("/themes/settings")
def display_theme_settings():
	config = current_app.config
	con = psycopg2.connect("dbname='"+config["DATABASE_NAME"]+"' user='"+config["DATABASE_USER"]+"' host='"+config["DATABASE_URL"]+"' password='"+config["DATABASE_PASSWORD"]+"'")
	cur = con.cursor()
	post_types = PostTypes.get_post_type_list(None, con)

	# TODO get all settings related to active theme
	try:
		cur.execute("SELECT settings_name, display_name, settings_value, section_name FROM sloth_settings WHERE section_name IN (SELECT LOWER(settings_value) FROM sloth_settings WHERE settings_name = 'active_theme')")
	except expression as identifier:
		abort(500)
	cur.close()
	con.close()

	# TODO display settings page
	return render_template("theme_settings.html")



@themes.route("/themes/settings/save", methods = ['POST'])
def save_theme_settings():
	config = current_app.config
	con = psycopg2.connect("dbname='"+config["DATABASE_NAME"]+"' user='"+config["DATABASE_USER"]+"' host='"+config["DATABASE_URL"]+"' password='"+config["DATABASE_PASSWORD"]+"'")
	cur = con.cursor()
	post_types = PostTypes.get_post_type_list(None, con)


	# TODO update theme options in database
	# TODO regenerate files
	cur.close()
	con.close()