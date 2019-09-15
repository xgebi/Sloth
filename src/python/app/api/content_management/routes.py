from flask import render_template, request, flash, redirect, url_for, current_app, make_response, abort
import psycopg2
from psycopg2 import sql
import bcrypt
import json
import http.client
import os
from xml.dom import minidom
import dateutil.parser
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
	
	#process_attachments(attachments)
	process_posts(posts, connection)
	generator = PostsGenerator(current_app.config)
	generator.regenerate_all()
	return json.dumps({ "ok": True })

def process_attachments(items):
	conn = {}
	for item in items:
		if conn == {}:
			conn = http.client.HTTPSConnection(item.getElementsByTagName('guid')[0].firstChild.wholeText[item.getElementsByTagName('guid')[0].firstChild.wholeText.find('//') + 2:item.getElementsByTagName('guid')[0].firstChild.wholeText.find('/', 8)])
		conn.request("GET", item.getElementsByTagName('guid')[0].firstChild.wholeText[item.getElementsByTagName('guid')[0].firstChild.wholeText.find('/', 8):])
		res = conn.getresponse()
		print(res.status, res.reason)
		
		data = res.read()

		with open(os.path.join(current_app.config["OUTPUT_PATH"], "sloth-content", item.getElementsByTagName('guid')[0].firstChild.wholeText[item.getElementsByTagName('guid')[0].firstChild.wholeText.rfind('/') + 1:]), 'wb') as f:
			f.write(data)
	if conn:
		conn.close()

def process_posts(items, connection):
	try:
		cur = connection.cursor()
		for item in items:
			#	title
			title = item.getElementsByTagName('title')[0].firstChild.wholeText
			#	link
			link = item.getElementsByTagName('link')[0].firstChild.wholeText
			#	pubDate or wp:post_date
			pub_date = dateutil.parser.parse(item.getElementsByTagName('pubDate')[0].firstChild.wholeText)
			#	dc:creator (CDATA)
			creator = item.getElementsByTagName('dc:creator')[0].firstChild.wholeText
			#	content:encoded (CDATA)
			content = item.getElementsByTagName('content:encoded')[0].firstChild.wholeText if item.getElementsByTagName('content:encoded')[0].firstChild is not None else ""
			#	wp:status (CDATA) (publish -> published, draft, scheduled?, private -> published)
			status = item.getElementsByTagName('wp:status')[0].firstChild.wholeText
			#	wp:post_type (attachment, nav_menu_item, illustration, page, post)
			post_type = item.getElementsByTagName('wp:post_type')[0].firstChild.wholeText
			#	category domain (post_tag, category) nicename
			categories = []
			tags = []
			for thing in item.getElementsByTagName('category'):
				domain = thing.getAttribute('domain')
				if (domain == 'post_tag'):
					tag.append(thing.getAttribute('nicename'))
				if (domain == 'category'):
					tag.append(thing.getAttribute('nicename'))



			cur.execute(
				sql.SQL("INSERT INTO sloth_posts (uuid, title, slug, content, post_type, post_status, update_date) VALUES (%s, %s, %s, %s, %s, 'draft', %s)"),
				[str(uuid.uuid4()), draft['title'], slug, draft['text'], draft['postType'], time() * 1000]
			)
			
			
			# post_type character varying(200), needs processing
			# author character varying(200) NULL, needs processing
			# publish_date double precision,
			# update_date double precision,
			# post_status character varying(10),
			# tags text[],
			# categories text[],

			connection.commit()
		cur.close()
	except Exception as e:
		print("117")
		print(e)
		abort(500)