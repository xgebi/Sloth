from flask import request, flash, url_for, current_app, make_response, abort
import psycopg2
from psycopg2 import sql
import bcrypt
import json
import http.client
import os
import re
from xml.dom import minidom
import dateutil.parser
import uuid
import traceback
from app.posts.post_types import PostTypes
from app.authorization.authorize import authorize_rest
from app.utilities.db_connection import db_connection
from app.posts.posts_generator import PostsGenerator

from app.api.content_management import content_management


@content_management.route("/api/content/information", methods=["GET"])
@authorize_rest(1)
@db_connection
def show_content(*args, connection=None, **kwargs):
	if connection is None:
		abort(500)

	post_types = PostTypes()
	post_types_result = post_types.get_post_type_list(connection)

	cur = connection.cursor()

	raw_items = []
	try:		
		cur.execute(
			"SELECT settings_name, display_name, settings_value, settings_value_type FROM sloth_settings WHERE settings_type = 'sloth'"
		)
		raw_items = cur.fetchall()
	except Exception as e:
		print("db error a")
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

	return json.dumps({"post_types": post_types_result, "settings": items})


@content_management.route("/api/content/import/wordpress", methods=["PUT", "POST"])
@authorize_rest(1)
@db_connection
def import_wordpress_content(*args, connection=None, **kwargs):
	if connection is None:
		return
	
	xml_data = minidom.parseString(json.loads(request.data)["data"])
	base_import_link = xml_data.getElementsByTagName('wp:base_blog_url')[0].firstChild.wholeText
	items = xml_data.getElementsByTagName('item')
	posts = []
	attachments = []
	for item in items:
		post_type = item.getElementsByTagName('wp:post_type')[0].firstChild.wholeText
		if post_type == 'attachment':
			attachments.append(item)
		if post_type == 'post' or post_type == 'page':
			posts.append(item)
	
	process_attachments(attachments, connection)
	process_posts(posts, connection, base_import_link)
	generator = PostsGenerator()
	generator.run(posts=True)
	return json.dumps({"ok": True})


def process_attachments(items, connection):
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
		meta_infos = item.getElementsByTagName('wp:postmeta')
		alt = ""
		for info in meta_infos:
			if (info.getElementsByTagName('wp:meta_key')[0].firstChild.wholeText == '_wp_attachment_image_alt'):
				alt = info.getElementsByTagName('wp:meta_value')[0].firstChild.wholeText
		try:
			cur = connection.cursor()
			cur.execute(
				sql.SQL("INSERT INTO sloth_media VALUES (%s, %s, %s)"),
				[uuid.uuid4(), os.path.join(current_app.config["OUTPUT_PATH"], "sloth-content", item.getElementsByTagName('guid')[0].firstChild.wholeText[item.getElementsByTagName('guid')[0].firstChild.wholeText.rfind('/') + 1:]), alt, int(item.getElementsByTagName('wp:post_id')[0].firstChild.wholeText)]
			)
			raw_post_types = cur.fetchall()
			connection.commit()
		except Exception as e:
			print("100")
			print(traceback.format_exc())
			abort(500)

		cur.close()
	if conn:
		conn.close()

def process_posts(items, connection, base_import_link):
	try:
		cur = connection.cursor()
		cur.execute(
			sql.SQL("SELECT slug, uuid FROM sloth_post_types")
		)
		raw_post_types = cur.fetchall()
		post_types = {}
		for post_type in raw_post_types:
			post_types[post_type[0]] = post_type[1]
		raw_post_types = None
		for item in items:
			#	title
			title = item.getElementsByTagName('title')[0].firstChild.wholeText
			slug = re.sub('[^0-9a-zA-Z\-]+', '', re.sub(r'\s+', '-', title)).lower()
			cur.execute(
				sql.SQL("SELECT count(slug) FROM sloth_posts WHERE slug LIKE %s OR slug LIKE %s"),
				[f"{'slug'}-%", f"{'slug'}%"]
			)
			similar = cur.fetchone()[0]
			print(slug, similar)
			if int(similar) > 0:
				slug = f"{slug}-{str(int(similar) + 1)}"
				
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
			if status == "publish" or status == "private":
				status = "published"
			#	wp:post_type (attachment, nav_menu_item, illustration, page, post)
			post_type = item.getElementsByTagName('wp:post_type')[0].firstChild.wholeText
			#	category domain (post_tag, category) nicename
			categories = []
			tags = []
			for thing in item.getElementsByTagName('category'):
				domain = thing.getAttribute('domain')
				if (domain == 'post_tag'):
					tags.append(thing.getAttribute('nicename'))
				if (domain == 'category'):
					categories.append(thing.getAttribute('nicename'))
			# TODO match tags and categories ?
			meta_infos = item.getElementsByTagName('wp:postmeta')
			thumbnail_id = ""
			for info in meta_infos:
				if (info.getElementsByTagName('wp:meta_key')[0].firstChild.wholeText == '_thumbnail_id'):
					thumbnail_id = info.getElementsByTagName('wp:meta_value')[0].firstChild.wholeText

			if not post_types[post_type]:
				cur.execute(
					sql.SQL("INSERT INTO sloth_post_types (uuid, slug, display_name, tags_enabled, categories_enabled, archive_enabled) VALUES (%s, %s, %s, true, true, true) RETURNING slug, uuid"),
					[str(uuid.uuid4()), post_type, post_type]
				)
				returned = cur.fetchone()
				post_types[returned[0]] = returned[1]
			# uuid, title, slug, content, post_type, post_status, update_date, tags, categories
			cur.execute(
				sql.SQL("INSERT INTO sloth_posts (uuid, title, slug, content, post_type, post_status, update_date, tags, categories, thumbnail) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, (SELECT uuid FROM sloth_media WHERE wp_id = %s))"),
				[str(uuid.uuid4()), title, slug, content, post_types[post_type], status, pub_date.timestamp() * 1000, tags if not tags is [] else None, categories if not categories is [] else None, thumbnail_id]
			)
		connection.commit()
		cur.close()
	except Exception as e:
		print("117")
		print(traceback.format_exc())
		abort(500)