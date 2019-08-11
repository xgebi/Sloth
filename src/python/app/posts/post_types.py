from flask import abort
import psycopg2
from psycopg2 import sql, errors

class PostTypes:
	def __init__(self):
		pass
		# Placeholder for the future

	def get_post_type_list(self, connection):
		cur = connection.cursor()
		raw_items = []
		try:
			cur.execute(
				"SELECT uuid, display_name FROM sloth_post_types"
			)
			raw_items = cur.fetchall()
		except Exception as e:
			abort(500)
		cur.close()
		items = []
		for item in raw_items:
			items.append({
				"uuid": item[0],
				"displayName": item[1]
			})
		return items

	def get_post_type(self, connection, post_type_id):
		cur = connection.cursor()
		raw_items = []
		try:
			cur.execute(
				sql.SQL("SELECT uuid, display_name, slug, tags_enabled, categories_enabled, archive_enabled FROM sloth_post_types WHERE uuid = %s"), [post_type_id]
			)
			raw_items = cur.fetchall()
		except Exception as e:
			abort(500)
		cur.close()
		items = []
		for item in raw_items:
			items.append({
				"uuid": item[0],
				"displayName": item[1],
				"slug": item[2],
				"tagsEnabled": item[3],
				"categoriesEnabled": item[4],
				"archiveEnabled": item[5]
			})
		return items