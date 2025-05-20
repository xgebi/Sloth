import psycopg
from flask import request, abort, make_response
import json
import uuid
import os
from app.back_office.post.post_types import PostTypes
from app.authorization.authorize import authorize_rest, authorize_web
from app.utilities.utilities import get_default_language
from app.utilities.db_connection import db_connection
from app.toes.toes import render_toe_from_path
from app.toes.hooks import Hooks

from app.routes.settings.language_settings import language_settings


@language_settings.route("/settings/language", methods=["GET"])
@authorize_web(1)
@db_connection
def show_language_settings(*args, permission_level: int, connection: psycopg.Connection, **kwargs):
	post_types = PostTypes()
	post_types_result = post_types.get_post_type_list(connection)

	try:
		with connection.cursor(row_factory=psycopg.rows.dict_row) as cur:
			cur.execute("""SELECT uuid, short_name, long_name FROM sloth_language_settings""")
			languages = cur.fetchall()
	except Exception as e:
		print(e)
		connection.close()
		abort(500)

	default_lang = get_default_language(connection=connection)
	connection.close()

	for lang in languages:
		languages.update({
			"default": lang['uuid'] == default_lang
		})

	return render_toe_from_path(
		path_to_templates=os.path.join(os.getcwd(), 'app', 'templates'),
		template="language.toe.html",
		data={
			"title": "Languages",
			"post_types": post_types_result,
			"permission_level": permission_level,
			"default_lang": default_lang,
			"languages": languages
		},
		hooks=Hooks()
	)


@language_settings.route("/api/settings/language/<lang_id>/save", methods=["POST", "PUT"])
@authorize_rest(1)
@db_connection
def save_language_info(*args, connection: psycopg.Connection, lang_id: str, **kwargs):
	filled = json.loads(request.data)

	cur = connection.cursor()
	try:
		if lang_id.startswith("new-"):
			cur.execute("""INSERT INTO sloth_language_settings VALUES (%s, %s, %s)
                RETURNING uuid, short_name, long_name;""",
						(str(uuid.uuid4()), filled["shortName"], filled["longName"]))
		else:
			cur.execute("""UPDATE sloth_language_settings SET short_name = %s, long_name = %s WHERE uuid = %s
                RETURNING uuid, short_name, long_name;""",
						(filled["shortName"], filled["longName"], lang_id))
		connection.commit()
		temp_result = cur.fetchone()
	except Exception as e:
		print(e)
		connection.close()
		abort(500)

	connection.close()

	result = {
		"uuid": temp_result[0],
		"shortName": temp_result[1],
		"longName": temp_result[2]
	}
	if lang_id.startswith("new-"):
		result["new"] = True
		result["oldUuid"] = lang_id

	response = make_response(json.dumps(result))
	response.headers['Content-Type'] = 'application/json'
	code = 200

	return response, code


@language_settings.route("/api/settings/language/<lang_id>/delete", methods=["DELETE"])
@authorize_rest(1)
@db_connection
def delete_language(*args, connection: psycopg.Connection, lang_id: str, **kwargs):
	try:
		with connection.cursor() as cur:
			cur.execute("""DELETE FROM sloth_language_settings WHERE uuid = %s;""",
						(lang_id, ))
			connection.commit()
		connection.close()

		response = make_response(json.dumps({
			"uuid": lang_id,
			"deleted": True
		}))
		code = 200
	except Exception as e:
		print(e)
		connection.close()
		response = make_response(json.dumps({
			"uuid": lang_id,
			"deleted": False
		}))
		code = 200

	response.headers['Content-Type'] = 'application/json'
	return response, code


@language_settings.route("/api/languages", methods=['GET'])
@authorize_rest(0)
@db_connection
def get_language_list(*args, connection: psycopg.Connection, **kwargs):
	try:
		with connection.cursor(row_factory=psycopg.rows.dict_row) as cur:
			cur.execute("""SELECT uuid, long_name as longName, short_name as shortName FROM sloth_language_settings;""")
			res = cur.fetchall()
			for lang in res:
				lang.update({'default': False})
			default_lang = get_default_language(connection=connection)
			for lang in res:
				if lang["uuid"] == default_lang["uuid"]:
					lang["default"] = True
			return json.dumps(res), 200
	except Exception as e:
		print(e)
		return json.dumps({"error": "Cannot fetch languages"}), 500
