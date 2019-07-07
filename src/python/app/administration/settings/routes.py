from flask import render_template, request, flash, redirect, url_for, current_app, abort
import psycopg2
import os
import json

from app.administration.settings import settings as sloth_settings

@sloth_settings.route('/settings')
def settings():
	config = current_app.config
	con = psycopg2.connect("dbname='"+config["DATABASE_NAME"]+"' user='"+config["DATABASE_USER"]+"' host='"+config["DATABASE_URL"]+"' password='"+config["DATABASE_PASSWORD"]+"'")
	cur = con.cursor()

	raw_items = []

	try:            
		cur.execute(
			"SELECT settings_name, display_name, settings_value FROM sloth_settings WHERE section_id = 'main'"
		)
		raw_items = cur.fetchall()
	except Exception as e:
		abort(500)
	items = {item[0]:item for item in raw_items}
	return render_template('settings.html', sloth_settings = items)

@sloth_settings.route('/settings/save')
def save_settings(self, settings):
	pass
	# TODO privilege checks
	# TODO get all post args
	# TODO update settings table in database
	# TODO redirect to settings page display