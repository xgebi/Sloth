from flask import render_template, request, flash, redirect, url_for, current_app, make_response, abort
import psycopg2
from psycopg2 import sql
import bcrypt
import json
from xml.dom import minidom
from app.posts.post_types import PostTypes
from app.authorization.authorize import authorize
from app.utilities.db_connection import db_connection
from app.posts.posts_generator import PostsGenerator

from app.api.content_management import content_management

@content_management.route("/api/content/information", methods=["GET"])
@authorize(1)
@db_connection
def show_content(*args, connection=None, **kwargs):
	if connection is None:
		abort(500)

	postTypes = PostTypes()
	postTypesResult = postTypes.get_post_type_list(connection)

	cur = connection.cursor()

	raw_items = []
	try:		
		cur.execute(
			"SELECT settings_name, display_name, settings_value, settings_value_type FROM sloth_settings WHERE settings_type = 'sloth'"
		)
		raw_items = cur.fetchall()
	except Exception as e:
		print("db error")
		abort(500)

	cur.close()
	connection.close()

	items = []
	for item in raw_items:
		items.append({
			"settingsName": item[0],
			"displayName": item[1],
			"settingsValue": item[2],
			"settingsValueType": item[3]
		})

	return json.dumps({ "postTypes": postTypesResult, "settings": items })

@content_management.route("/api/content/import/wordpress", methods=["PUT", "POST"])
@authorize(1)
@db_connection
def import_wordpress_content(*args, connection=None, **kwargs):
	if connection is None:
		return

	xml_data = minidom.parseString(request.data)
	items = xml_data.getElementsByTagName('item')
	posts = []
	attachments = []
	for item in items:
		post_type = item.getElementsByTagName('wp:post_type')[0].firstChild.wholeText
		if post_type == 'attachment':
			attachments.append(item)
		if post_type == 'post' or post_type == 'page':
			posts.append(item)
	
	process_attachments(attachments)
	process_posts(posts, connection)
	generator = PostsGenerator(current_app.config)
	generator.regenerate_all()
	return json.dumps({ "ok": True })

def process_attachments(items):
	pass

def process_posts(items, connection):
	try:
		cur = connection.cursor()
		for item in items:
			#	title
			title = item.getElementsByTagName('title')[0]
			#	link
			link = item.getElementsByTagName('link')[0]
			#	pubDate or wp:post_date

			#	dc:creator (CDATA)
			#	content:encoded (CDATA)
			#	wp:post_date (CDATA)
			#	wp:status (CDATA) (publish, draft, scheduled?)
			#	wp:post_type (attachment, nav_menu_item, illustration, page, post)
			#	category domain (post_tag, category) nicename
			
		cur.close()
	except Exception as e:
		print("db error")
		abort(500)