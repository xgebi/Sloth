from flask import abort, make_response, request
from app.authorization.authorize import authorize_web, authorize_rest
from app.toes.hooks import Hooks
from app.utilities.db_connection import db_connection
from app.utilities.utilities import get_default_language
import json
import re
import datetime
import traceback
import os
import uuid
from time import time
import psycopg
from typing import Tuple, List, Dict, Optional

from app.back_office.post.post_types import PostTypes
from app.toes.toes import render_toe_from_path
from app.dashboard import dashboard


@dashboard.route('/dashboard')
@authorize_web(permission_level=0)
@db_connection
def show_dashboard(*args, permission_level: int, connection: psycopg.Connection, **kwargs) -> str:
	"""
	Renders dashboard page

	:param args:
	:param permission_level:
	:param connection:
	:param kwargs:
	:return:
	"""
	post_types = PostTypes()
	post_types_result = post_types.get_post_type_list(connection)
	default_language = get_default_language(connection=connection)

	recent_posts, upcoming_posts, drafts, messages = fetch_dashboard_data(connection=connection)

	return render_toe_from_path(
		path_to_templates=os.path.join(os.getcwd(), 'app', 'templates'),
		template="dashboard.toe.html",
		data={
			"title": "Dashboard",
			"post_types": post_types_result,
			"permission_level": permission_level,
			"messages": messages,
			"recent_posts": recent_posts,
			"drafts": drafts,
			"upcoming_posts": upcoming_posts,
			"default_lang": default_language
		},
		hooks=Hooks()
	)


def fetch_dashboard_data(*args, connection: psycopg.Connection, to_json: Optional[bool] = False, **kwargs) \
		-> Tuple[List[Dict], List[Dict], List[Dict], List[Dict]]:
	"""
	Fetches data required to display in dashboard

	:param args:
	:param connection:
	:param to_json:
	:param kwargs:
	:return:
	"""
	try:
		with connection.cursor(row_factory=psycopg.rows.dict_row) as cur:
			cur.execute(
				"""SELECT A.uuid, A.title, A.publish_date as date, B.display_name 
					FROM sloth_posts AS A INNER JOIN sloth_post_types AS B ON B.uuid = A.post_type 
					WHERE post_status = %s ORDER BY A.publish_date DESC LIMIT 10;""",
				('published',)
			)
			recent_posts = cur.fetchall()

			cur.execute(
				"""SELECT A.uuid, A.title, A.publish_date as date, B.display_name 
					FROM sloth_posts AS A INNER JOIN sloth_post_types AS B ON B.uuid = A.post_type 
					WHERE post_status = %s ORDER BY A.publish_date LIMIT 10;""",
				('scheduled',)
			)
			upcoming_posts = cur.fetchall()

			cur.execute(
				"""SELECT A.uuid, A.title, A.update_date as date, B.display_name 
					FROM sloth_posts AS A INNER JOIN sloth_post_types AS B ON B.uuid = A.post_type 
					WHERE post_status = %s ORDER BY A.update_date DESC LIMIT 10;""",
				('draft',)
			)
			drafts = cur.fetchall()

			cur.execute(
				"""SELECT uuid, sent_date, status 
					FROM sloth_messages WHERE status != 'deleted' ORDER BY sent_date DESC LIMIT 10"""
			)
			raw_messages = cur.fetchall()

	except psycopg.errors.DatabaseError as e:
		print(traceback.format_exc())
		abort(500)

	messages = []
	if to_json:
		recent_posts = format_post_data_json(recent_posts)
		upcoming_posts = format_post_data_json(upcoming_posts)
		drafts = format_post_data_json(drafts)
		for msg in raw_messages:
			messages.append({
				"uuid": msg['uuid'],
				"sentDate": datetime.datetime.fromtimestamp(float(msg['sent_date']) / 1000.0).strftime("%Y-%m-%d %H:%M"),
				"status": msg['status']
			})
	else:
		recent_posts = format_post_data(recent_posts)
		upcoming_posts = format_post_data(upcoming_posts)
		drafts = format_post_data(drafts)
		for msg in raw_messages:
			messages.append({
				"uuid": msg['uuid'],
				"sent_date": datetime.datetime.fromtimestamp(float(msg['sent_date']) / 1000.0).strftime("%Y-%m-%d %H:%M"),
				"status": msg['status']
			})

	return recent_posts, upcoming_posts, drafts, messages


@dashboard.route("/api/dashboard-information")
@authorize_rest(0)
@db_connection
def dashboard_information(*args, connection: psycopg.Connection, **kwargs):
	"""
	API end point for getting dashboard information

	:param args:
	:param connection:
	:param kwargs:
	:return:
	"""
	post_types = PostTypes()
	post_types_result = post_types.get_post_type_list(connection)

	recent_posts, upcoming_posts, drafts, messages = fetch_dashboard_data(connection=connection, to_json=True)

	response = make_response(json.dumps({
		"post_types": post_types_result,
		"recentPosts": recent_posts,
		"upcomingPosts": upcoming_posts,
		"drafts": drafts,
		"messages": messages,
	}))
	code = 200

	response.headers['Content-Type'] = 'application/json'
	return response, code


@dashboard.route("/api/dashboard-information/create-draft", methods=["POST"])
@authorize_rest(0)
@db_connection
def create_draft(*args, connection: psycopg.Connection, **kwargs):
	"""
	API end point for quick creation of draft

	:param args:
	:param connection:
	:param kwargs:
	:return:
	"""
	draft = json.loads(request.data)

	slug = re.sub('\s+', '-', draft['title'])
	slug = re.sub('[^0-9a-zA-Z\-]+', '', slug)

	try:
		with connection.cursor(row_factory=psycopg.rows.dict_row) as cur:
			cur.execute("""INSERT INTO sloth_posts (uuid, title, slug, content, post_type, post_status, update_date, lang) 
                    VALUES (%s, %s, %s, %s, %s, 'draft', %s, 
                    (SELECT settings_value FROM sloth_settings WHERE settings_name = 'main_language'))""",
						(str(uuid.uuid4()), draft['title'], slug, draft['text'], draft['postType'], time() * 1000)
						)
			connection.commit()
			cur.execute("SELECT uuid, title, publish_date, post_type FROM sloth_posts WHERE post_status = %s LIMIT 10",
						('draft', )
						)
			drafts = cur.fetchall()
		response = make_response(json.dumps({
			"drafts": format_post_data(drafts)
		}))
		code = 200
	except Exception as e:
		print(traceback.format_exc())
		response = make_response(json.dumps({
			"error": True
		}))
		code = 500
	connection.close()
	response.headers['Content-Type'] = 'application/json'
	return response, code


def format_post_data_json(post_arr: List) -> List:
	"""
	Formats unnamed list of lists to list of dicts in JSON format naming conventions

	:param post_arr:
	:return:
	"""
	posts = []
	for post in post_arr:
		posts.append({
			"uuid": post['uuid'],
			"title": post['title'],
			"publishDate": post['date'],
			"formattedPublishDate": datetime.datetime.fromtimestamp(float(post['date']) / 1000.0).strftime("%Y-%m-%d %H:%M"),
			# "postType": post[3] # TODO investigate this, it makes no sense
		})
	return posts


def format_post_data(post_arr: List) -> List:
	"""
		Formats unnamed list of lists to list of dicts

		:param post_arr:
		:return:
		"""
	posts = [{
		"uuid": post['uuid'],
		"title": post['title'],
		"publish_date": post['publish_date'],
		"formatted_publish_date": datetime.datetime.fromtimestamp(float(post['publish_date']) / 1000.0).strftime("%Y-%m-%d %H:%M"),
		"post_type": post['post_type']
	} for post in post_arr]
	return posts
