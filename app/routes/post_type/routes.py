import json
import psycopg
import uuid
from flask import request, abort, redirect, render_template

from app.authorization.authorize import authorize_web, authorize_rest
from app.back_office.post.post_generator import PostGenerator
from app.back_office.post.post_types import PostTypes
from app.routes.post_type import post_type
from app.utilities.db_connection import db_connection
from app.utilities.utilities import get_default_language


@post_type.route("/post-types")
@authorize_web(1)
@db_connection
def show_post_types(*args, permission_level: int, connection: psycopg.Connection, **kwargs):
	post_types = PostTypes()
	post_types_result = post_types.get_post_type_list(connection)
	default_lang = get_default_language(connection=connection)
	connection.close()

	return render_template(
		"post-types-list.html",
		post_types=post_types_result,
		permission_level=permission_level,
		default_lang=default_lang
	)


@post_type.route("/post-type/new", methods=["GET"])
@authorize_web(1)
@db_connection
def new_post_type_page(*args, permission_level: int, connection: psycopg.Connection, **kwargs):
	post_types = PostTypes()
	post_types_result = post_types.get_post_type_list(connection)

	pt = {
		"uuid": uuid.uuid4()
	}
	default_lang = get_default_language(connection=connection)
	connection.close()
	return render_template(
		"post-type.html",
		post_types=post_types_result,
		permission_level=permission_level,
		post_type=type,
		new=True,
		pt=pt,
		default_lang=default_lang
	)


@post_type.route("/post-type/<post_type_id>", methods=["GET"])
@authorize_web(1)
@db_connection
def show_post_type(*args, permission_level: int, connection: psycopg.Connection, post_type_id: str, **kwargs):
	post_types = PostTypes()
	post_types_result = post_types.get_post_type_list(connection)

	pt = post_types.get_post_type(connection, post_type_id)
	default_lang = get_default_language(connection=connection)
	connection.close()
	return render_template(
		"post-type.html",
		post_types=post_types_result,
		permission_level=permission_level,
		pt=pt,
		default_lang=default_lang
	)


@post_type.route("/post-type/<post_type_id>", methods=["POST", "PUT"])
@authorize_web(1)
@db_connection
def save_post_type(*args, connection: psycopg.Connection, post_type_id: str, **kwargs):
	post_types = PostTypes()

	updated_post_type = request.form
	existing_post_type = post_types.get_post_type(connection, post_type_id)

	# 1. save to database
	try:
		with connection.cursor() as cur:
			cur.execute("""UPDATE sloth_post_types 
                    SET slug = %s, display_name = %s, tags_enabled = %s, 
                    categories_enabled = %s, archive_enabled = %s
                    WHERE uuid = %s;""",
						(updated_post_type["slug"], updated_post_type["display_name"],
						 updated_post_type["tags_enabled"], updated_post_type["categories_enabled"],
						 updated_post_type["archive_enabled"], post_type_id))
			connection.commit()
	except Exception as e:
		print(e)
		connection.close()
		abort(500)

	gen = PostGenerator(connection)
	run_gen = False
	# 2. if slug or display name changed
	if updated_post_type['slug'] != existing_post_type['slug'] \
			or updated_post_type['display_name'] != existing_post_type['display_name']:
		# a. delete post type
		gen.delete_post_type_post_files(existing_post_type)
		run_gen = True
	# 3. Categories/Tags/Archive changed to True
	if (updated_post_type['categories_enabled'] and not existing_post_type['categories_enabled']) \
			or (updated_post_type['tags_enabled'] and not existing_post_type['tags_enabled']) \
			or (updated_post_type['archive_enabled'] and not existing_post_type['archive_enabled']):
		run_gen = True
	# 6. Categories changed to False
	if updated_post_type['categories_enabled'] and not existing_post_type['categories_enabled']:
		# a. delete categories
		gen.delete_taxonomy_files(existing_post_type, 'category')
		run_gen = True
	# 7. Tags changed to False
	if updated_post_type['tags_enabled'] and not existing_post_type['tags_enabled']:
		# a. delete tags
		gen.delete_taxonomy_files(existing_post_type, 'tags')
		run_gen = True
	# 8. Archive changed to False
	if updated_post_type['archive_enabled'] and not existing_post_type['archive_enabled']:
		# a. delete archive
		gen.delete_archive_for_post_type(existing_post_type)

	if run_gen:
		if gen.run(post_type=updated_post_type):
			return redirect(f"/post-type/{post_type_id}")
		return redirect(f"/post-type/{post_type_id}?error=regenerating")

	return redirect(f"/post-type/{post_type_id}")


@post_type.route("/post-type/<post_type_id>/create", methods=["POST", "PUT"])
@authorize_web(1)
@db_connection
def create_post_type(*args, connection: psycopg.Connection, post_type_id: str, **kwargs):
	new_post_type = request.form

	# 1. save to database
	try:
		with connection.cursor() as cur:
			cur.execute("""INSERT INTO sloth_post_types VALUES (%s, %s, %s, %s, %s, %s);""",
						(post_type_id, new_post_type["slug"], new_post_type["display_name"],
						 True if "tags_enabled" in new_post_type else False,
						 True if "categories_enabled" in new_post_type else False,
						 True if "archive_enabled" in new_post_type else False))
			cur.execute("""INSERT INTO sloth_post_formats (uuid, slug, display_name, post_type, deletable) 
            VALUES (%s, %s, %s, %s, %s)""",
						(str(uuid.uuid4()), "none", "None", post_type_id, False))
			connection.commit()
	except Exception as e:
		print(e)
		connection.close()
		abort(500)

	connection.close()
	return redirect(f"/post-type/{post_type_id}")


@post_type.route("/api/post-type/delete", methods=["DELETE"])
@authorize_rest(1)
@db_connection
def delete_post_type(*args, connection: psycopg.Connection, **kwargs):
	data = json.loads(request.data)

	if data["action"] == "delete":
		try:
			with connection.cursor() as cur:
				cur.execute("""DELETE FROM sloth_posts WHERE post_type = %s""",
							(data["current"], ))
				connection.commit()
		except Exception as e:
			print(e)
	else:
		try:
			with connection.cursor() as cur:
				cur.execute("""UPDATE sloth_posts SET post_type = %s  WHERE post_type = %s""",
							(data["action"], data["current"]))
				connection.commit()
		except Exception as e:
			print(e)
	try:
		with connection.cursor() as cur:
			cur.execute("""DELETE FROM sloth_post_types WHERE uuid = %s""",
						(data["current"], ))
			connection.commit()
	except Exception as e:
		print(e)

	if data["action"] != "delete":
		gen = PostGenerator(connection=connection)
		gen.run(post_type=data["action"])
	else:
		connection.close()

	return json.dumps({"deleted": True})


@post_type.route("/api/post-types")
@authorize_rest(0)
@db_connection
def get_post_types(*args, permission_level: int, connection: psycopg.Connection, **kwargs):
	post_types = PostTypes()
	post_types_result = post_types.get_post_type_list_as_json(connection)
	connection.close()

	return json.dumps(post_types_result), 200
