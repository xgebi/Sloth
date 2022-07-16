import psycopg
from flask import abort


class PostTypes:
	def __init__(self):
		pass

	# Placeholder for the future

	def get_post_type_list(self, connection: psycopg.Connection):
		with connection.cursor(row_factory=psycopg.rows.dict_row) as cur:
			raw_items = []
			try:
				cur.execute(
					"""SELECT uuid, slug, display_name, tags_enabled, categories_enabled, archive_enabled 
							FROM sloth_post_types"""
				)
				items = cur.fetchall()
			except psycopg.errors.DatabaseError as e:
				abort(500)
			cur.close()

			return items

	def get_post_type_list_as_json(self, connection: psycopg.Connection):
		with connection.cursor(row_factory=psycopg.rows.dict_row) as cur:
			items = []
			try:
				cur.execute(
					"""SELECT uuid, slug, display_name, tags_enabled, categories_enabled, archive_enabled 
							FROM sloth_post_types"""
				)
				items = cur.fetchall()
			except psycopg.errors.DatabaseError as e:
				abort(500)
			cur.close()

			return [{
				"uuid": item['uuid'],
				"slug": item['slug'],
				"displayName": item['display_name'],
				"tagsEnabled": item['tags_enabled'],
				"categoriesEnabled": item['categories_enabled'],
				"archiveEnabled": item['archive_enabled']
			} for item in items]

	def get_post_type(self, connection, post_type_id):
		try:
			with connection.cursor(row_factory=psycopg.rows.dict_row) as cur:
				cur.execute(
					"""SELECT uuid, display_name, slug, tags_enabled, categories_enabled, archive_enabled 
					FROM sloth_post_types WHERE uuid = %s""", (post_type_id, ))
				item = cur.fetchone()
				cur.close()
				return item
		except Exception as e:
			abort(500)

