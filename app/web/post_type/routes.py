from flask import request, flash, url_for, current_app, abort, redirect, render_template
from app.utilities.db_connection import db_connection
from app.authorization.authorize import authorize_web
from app.posts.post_types import PostTypes
from app.posts.posts_generator import PostsGenerator
import psycopg2
from psycopg2 import sql
import datetime
import uuid

from app.web.post_type import post_type


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
def new_post_type(*args, permission_level, connection, **kwargs):
    if connection is None:
        return redirect("/database-error")

    post_types = PostTypes()
    post_types_result = post_types.get_post_type_list(connection)

    type = {
        "uuid": uuid.uuid4()
    }

    return render_template(
        "post-type.html",
        post_types=post_types_result,
        permission_level=permission_level,
        post_type=type,
        new=True
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
    post_types_result = post_types.get_post_type_list(connection)

    updated_post_type = request.form
    existing_post_type = post_types.get_post_type(connection, post_type_id)

    # ImmutableMultiDict([('display-name', 'Post'), ('slug', 'post'), ('categories-enabled', 'on'), ('tags-enabled', 'on'), ('archive-enabled', 'on')])
    # {'uuid': '1adbec5d-f4a1-401d-9274-3552f1219f36', 'display_name': 'Post', 'slug': 'post', 'tags_enabled': True, 'categories_enabled': True, 'archive_enabled': True}

    # 1. save to database
    cur = connection.cursor()
    try:
        cur.execute(
            sql.SQL("""UPDATE sloth_post_types 
                SET slug = %s, display_name = %s, tags_enabled = %s, 
                categories_enabled = %s, archive_enabled = %s
                WHERE uuid = %s;"""),
            [updated_post_type["slug"], updated_post_type["display-name"],
             updated_post_type["tags-enabled"], updated_post_type["categories-enabled"],
             updated_post_type["archive-enabled"], post_type_id]
        )
        connection.commit()
    except Exception as e:
        print(e)
        abort(500)
    cur.close()

    gen = PostsGenerator(connection)
    run_gen = False
    # 2. if slug or display name changed
    if updated_post_type['slug'] != existing_post_type['slug'] \
            or updated_post_type['display-name'] != existing_post_type['display_name']:
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
            run_gen = True

    if run_gen:
        gen.run(post_type=updated_post_type)

    return redirect(f"/post-type/{post_type_id}")


@post_type.route("/post-type/<post_type_id>/delete", methods=["POST", "PUT", "DELETE"])
@authorize_web(1)
@db_connection
def delete_post_type(*args, permission_level, connection, post_type_id, **kwargs):
    if connection is None:
        return redirect("/database-error")

    # 1. delete from database
    # 2. delete post type

    return redirect("/post-type")
