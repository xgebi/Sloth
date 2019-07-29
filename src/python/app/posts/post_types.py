from flask import abort
import psycopg2

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