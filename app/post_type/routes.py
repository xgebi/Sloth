from flask import request, abort, redirect, render_template

from app.post.post_generator import PostGenerator
from app.utilities.db_connection import db_connection
from app.authorization.authorize import authorize_web, authorize_rest
from app.post.post_types import PostTypes
from psycopg2 import sql
import json
import uuid

from app.post_type import post_type


@post_type.route("/post-types")
@authorize_web(1)
@db_connection
def show_post_types(*args, permission_level, connection, **kwargs):
    if connection is None:
        return redirect("/database-error")

    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)

    return render_template("post-types-list.html", post_types=post_types_result, permission_level=permission_level)


@post_type.route("/post-type/new", methods=["GET"])
@authorize_web(1)
@db_connection
def new_post_type_page(*args, permission_level, connection, **kwargs):
    if connection is None:
        return redirect("/database-error")

    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)

    pt = {
        "uuid": uuid.uuid4()
    }

    return render_template(
        "post-type.html",
        post_types=post_types_result,
        permission_level=permission_level,
        post_type=type,
        new=True,
        pt=pt
    )


@post_type.route("/post-type/<post_type_id>", methods=["GET"])
@authorize_web(1)
@db_connection
def show_post_type(*args, permission_level, connection, post_type_id, **kwargs):
    if connection is None:
        return redirect("/database-error")

    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)

    pt = post_types.get_post_type(connection, post_type_id)

    return render_template(
        "post-type.html",
        post_types=post_types_result,
        permission_level=permission_level,
        pt=pt
    )


@post_type.route("/post-type/<post_type_id>", methods=["POST", "PUT"])
@authorize_web(1)
@db_connection
def save_post_type(*args, permission_level, connection, post_type_id, **kwargs):
    if connection is None:
        return redirect("/database-error")

    post_types = PostTypes()

    updated_post_type = request.form
    existing_post_type = post_types.get_post_type(connection, post_type_id)

    # 1. save to database
    cur = connection.cursor()
    try:
        cur.execute(
            sql.SQL("""UPDATE sloth_post_types 
                SET slug = %s, display_name = %s, tags_enabled = %s, 
                categories_enabled = %s, archive_enabled = %s
                WHERE uuid = %s;"""),
            [updated_post_type["slug"], updated_post_type["display_name"],
             updated_post_type["tags_enabled"], updated_post_type["categories_enabled"],
             updated_post_type["archive_enabled"], post_type_id]
        )
        connection.commit()
    except Exception as e:
        print(e)
        abort(500)
    cur.close()

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
def create_post_type(*args, permission_level, connection, post_type_id, **kwargs):
    if connection is None:
        return redirect("/database-error")

    new_post_type = request.form

    # 1. save to database
    cur = connection.cursor()
    try:
        cur.execute(
            sql.SQL("""INSERT INTO sloth_post_types VALUES (%s, %s, %s, %s, %s, %s);"""),
            [post_type_id, new_post_type["slug"], new_post_type["display_name"],
             True if "tags_enabled" in new_post_type else False,
             True if "categories_enabled" in new_post_type else False,
             True if "archive_enabled" in new_post_type else False]
        )
        connection.commit()
    except Exception as e:
        print(e)
        abort(500)
    cur.close()

    return redirect(f"/post-type/{post_type_id}")


@post_type.route("/api/post-type/delete", methods=["DELETE"])
@authorize_rest(1)
@db_connection
def delete_post_type(*args, permission_level, connection, **kwargs):
    if connection is None:
        return redirect("/database-error")

    data = json.loads(request.data)
    cur = connection.cursor()
    if data["action"] == "delete":
        try:
            cur.execute(
                sql.SQL("""DELETE FROM sloth_posts WHERE post_type = %s"""),
                [data["current"]]
            )
        except Exception as e:
            print(e)
    else:
        try:
            cur.execute(
                sql.SQL("""UPDATE sloth_posts SET post_type = %s  WHERE post_type = %s"""),
                [data["action"], data["current"]]
            )
        except Exception as e:
            print(e)
    try:
        cur.execute(
            sql.SQL("""DELETE FROM sloth_post_types WHERE uuid = %s"""),
            [data["current"]]
        )
    except Exception as e:
        print(e)
    connection.commit()
    cur.close()
    if data["action"] != "delete":
        gen = PostGenerator(connection=connection)
        gen.run(post_type=data["action"])
    else:
        connection.close()

    return json.dumps({"deleted": True})
