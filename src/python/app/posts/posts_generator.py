import psycopg2
from psycopg2 import sql, errors
from flask import current_app
from jinja2 import Template

import threading
import time
import os
import math
from pathlib import Path

from app.utilities.db_connection import db_connection

class PostsGenerator:
	post = {}
	config = {}
	settings = {}
	is_runnable = True
	theme_path = ""
	connection = {}

	@db_connection
	def __init__(self, post, config, connection=None):
		if connection is None:
			self.is_runnable = False

		self.connection = connection
		self.post = post
		self.config = config
		cur = connection.cursor()
		try:
			cur.execute(
				sql.SQL("SELECT settings_name, settings_value, settings_value_type FROM sloth_settings WHERE settings_name = %s OR settings_type = %s"), ['active_theme', 'sloth']
			)
			raw_items = cur.fetchall()
			for item in raw_items:
				self.settings[str(item[0])] = {
					"settings_name": item[0],
					"settings_value": item[1],
					"settings_value_type": item[2]
				}
		except Exception as e:
			print(e)
		self.theme_path = Path(self.config["THEMES_PATH"], self.settings['active_theme']['settings_value'])

	def run(self):
		if not self.is_runnable:
			return
		
		t = threading.Thread(target=self.generateContent)
		t.start()

	def generateContent(self):
		self.generate_post()

		if (self.post["tags_enabled"]):
			self.generate_tags()
		
		#if (self.post["categories_enabled"]):
		#	generate_categories()
		
		#if (self.post["archive_enabled"]):
		#	generate_archive()
		
		# regenerate home if newly published

	def generate_post(self):
		post_path_dir = Path(self.config["OUTPUT_PATH"], self.post["post_type_slug"], self.post["slug"])
		self.theme_path = Path(self.config["THEMES_PATH"], self.settings['active_theme']['settings_value'])

		post_template_path = Path(self.theme_path, "post.html")
		if (Path(self.theme_path, "post-" + self.post["post_type_slug"] + ".html").is_file()):
			post_template_path = Path(self.theme_path, "post-" + self.post["post_type_slug"] + ".html")

		template = ""
		with open(post_template_path, 'r') as f:			
			template = Template(f.read())
		
		if not os.path.exists(post_path_dir):
			os.makedirs(post_path_dir)

		with open(os.path.join(post_path_dir, 'index.html'), 'w') as f:
			f.write(template.render(post=self.post, sitename=self.settings["sitename"]["settings_value"]))

	def generate_tags(self):
		if len(self.post["tags"]) == 0:
			return
		tags_list = self.post["tags"]
		tags_posts_list = {}

		for tag in tags_list:
			tags_posts_list[tag] = []
			try:
				cur = self.connection.cursor()
				cur.execute(
					sql.SQL("SELECT uuid, title, publish_date FROM sloth_posts WHERE post_type = %s AND %s = ANY (tags) AND post_status = %s"), [self.post["post_type"], tag, 'published']
				)
				raw_items = cur.fetchall()
				for item in raw_items:
					tags_posts_list[tag].append({
						"uuid": item[0],
						"title": item[1],
						"publish_date": item[2]
					})
				cur.close()
			except Exception as e:
				print(e)
		
		tag_template_path = Path(self.theme_path, "tag.html")
		if (Path(self.theme_path, "tag-" + self.post["post_type_slug"] + ".html").is_file()):
			tag_template_path = Path(self.theme_path, "tag-" + self.post["post_type_slug"] + ".html")
		elif (not tag_template_path.is_file()):
			tag_template_path = Path(self.theme_path, "archive.html")	

		template = ""
		with open(tag_template_path, 'r') as f:
			template = Template(f.read())		

		for tag in tags_list:
			post_path_dir = Path(self.config["OUTPUT_PATH"], self.post["post_type_slug"], 'tag')

			if not os.path.exists(post_path_dir):
				os.makedirs(post_path_dir)
			
			if not os.path.exists(os.path.join(post_path_dir, tag)):
				os.makedirs(os.path.join(post_path_dir, tag))
			
			for i in range(math.ceil(len(tags_posts_list[tag])/10)):
				if i > 0 and not os.path.exists(os.path.join(post_path_dir, tag, str(i))):
					os.makedirs(os.path.join(post_path_dir, tag, str(i)))
				
				with open(os.path.join(post_path_dir, tag, str(i) if i != 0 else '', 'index.html'), 'w') as f:
					lower = 10 * i
					upper = (10*i) + 10 if (10*i) + 10 < len(tags_posts_list[tag]) else len(tags_posts_list[tag])
					
					f.write(template.render(posts = tags_posts_list[tag][lower: upper], tag = tag, sitename=self.settings["sitename"]["settings_value"], page_name = "Tag: "+tag))

	def generate_categories(self):
		if len(self.post["categories"]) == 0:
			return
		categories_list = self.post["categories"]
		categories_posts_list = {}

		for category in categories_list:
			categories_posts_list[category] = []
			try:
				cur = self.connection.cursor()
				cur.execute(
					sql.SQL("SELECT uuid, title, publish_date FROM sloth_posts WHERE post_type = %s AND %s = ANY (tags) AND post_status = %s"), [self.post["post_type"], category, 'published']
				)
				raw_items = cur.fetchall()
				for item in raw_items:
					categories_posts_list[category].append({
						"uuid": item[0],
						"title": item[1],
						"publish_date": item[2]
					})
				cur.close()
			except Exception as e:
				print(e)

		category_template_path = Path(self.theme_path, "category.html")
		if (Path(self.theme_path, "category-" + self.post["post_type_slug"] + ".html").is_file()):
			category_template_path = Path(self.theme_path, "category-" + self.post["post_type_slug"] + ".html")
		elif (not category_template_path.is_file()):
			category_template_path = Path(self.theme_path, "archive.html")

		template = ""
		with open(category_template_path, 'r') as f:
			template = Template(f.read())

		for category in categories_list:
			post_path_dir = Path(self.config["OUTPUT_PATH"], self.post["post_type_slug"], 'category')

			if not os.path.exists(post_path_dir):
				os.makedirs(post_path_dir)
			
			if not os.path.exists(os.path.join(post_path_dir, category)):
				os.makedirs(os.path.join(post_path_dir, tag))
			
			for i in range(math.ceil(len(categories_posts_list[category])/10)):
				if i > 0 and not os.path.exists(os.path.join(post_path_dir, category, str(i))):
					os.makedirs(os.path.join(post_path_dir, tag, str(i)))
				
				with open(os.path.join(post_path_dir, category, str(i) if i != 0 else '', 'index.html'), 'w') as f:
					lower = 10 * i
					upper = (10*i) + 10 if (10*i) + 10 < len(categories_posts_list[category]) else len(categories_posts_list[category])
					
					f.write(template.render(posts = categories_posts_list[category][lower: upper], tag = category, sitename=self.settings["sitename"]["settings_value"], page_name = "Category: "+category))
	
	def generate_archive(self):
		tags_template_path = Path(self.theme_path, "archive.html")
		if (Path(self.theme_path, "archive-" + self.post["post_type_slug"] + ".html").is_file()):
			post_template_path = Path(self.theme_path, "archive-" + self.post["post_type_slug"] + ".html")

		template = ""
		with open(post_template_path, 'r') as f:
			template = Template(f.read())

		with open(os.path.join(post_path_dir, 'index.html'), 'w') as f:
			f.write(template.render())

		