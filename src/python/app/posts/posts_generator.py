import psycopg2
from psycopg2 import sql, errors
from flask import current_app
from jinja2 import Template
from xml.dom import minidom

import threading
import time
from datetime import datetime
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
		
		if (self.post["categories_enabled"]):
			self.generate_categories()
		
		if (self.post["archive_enabled"]):
			self.generate_archive()
		
		self.generate_home()

	# generate_post
	# generates a file with post data
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
					sql.SQL("SELECT uuid, title, publish_date FROM sloth_posts WHERE post_type = %s AND %s = ANY (categories) AND post_status = %s"), [self.post["post_type"], category, 'published']
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
				os.makedirs(os.path.join(post_path_dir, category))
			
			for i in range(math.ceil(len(categories_posts_list[category])/10)):
				if i > 0 and not os.path.exists(os.path.join(post_path_dir, category, str(i))):
					os.makedirs(os.path.join(post_path_dir, category, str(i)))
				
				with open(os.path.join(post_path_dir, category, str(i) if i != 0 else '', 'index.html'), 'w') as f:
					lower = 10 * i
					upper = (10*i) + 10 if (10*i) + 10 < len(categories_posts_list[category]) else len(categories_posts_list[category])
					
					f.write(template.render(posts = categories_posts_list[category][lower: upper], sitename=self.settings["sitename"]["settings_value"], page_name = "Category: "+category))
	
	def generate_archive(self):
		post_list = []
		try:
			cur = self.connection.cursor()
			cur.execute(
				sql.SQL("""SELECT A.uuid, 
							  A.title,
							  A.slug, 							   
							  A.content, 							   
							  A.publish_date, 							  
							  A.categories,						   
							  B.slug AS post_type_slug
						FROM sloth_posts AS A INNER JOIN sloth_post_types AS B ON B.uuid = A.post_type
						WHERE A.post_type = %s AND A.post_status = %s"""), [self.post["post_type"], 'published']
			)
			raw_items = cur.fetchall()
			for item in raw_items:
				post_list.append({
					"uuid": item[0],
					"title": item[1],
					"slug": item[2],
					"content": item[3],
					"publish_date": item[4],
					"categories": item[5],
					"post_type_slug": item[6]
				})
			cur.close()
		except Exception as e:
			print(e)

		archive_template_path = Path(self.theme_path, "archive.html")
		if (Path(self.theme_path, "archive-" + self.post["post_type_slug"] + ".html").is_file()):
			archive_template_path = Path(self.theme_path, "archive-" + self.post["post_type_slug"] + ".html")
		elif (not archive_template_path.is_file()):
			archive_template_path = Path(self.theme_path, "archive.html")

		template = ""
		with open(archive_template_path, 'r') as f:
			template = Template(f.read())

		post_path_dir = Path(self.config["OUTPUT_PATH"], self.post["post_type_slug"])

		if not os.path.exists(post_path_dir):
			os.makedirs(post_path_dir)
		
		for i in range(math.ceil(len(post_list)/10)):
			lower = 10 * i
			upper = (10*i) + 10 if (10*i) + 10 < len(post_list) else len(post_list)

			if i == 0:
				self.generate_rss(post_list[lower: upper], post_path_dir)

			if i > 0 and not os.path.exists(os.path.join(post_path_dir, str(i))):
				os.makedirs(os.path.join(post_path_dir, str(i)))
			
			with open(os.path.join(post_path_dir, str(i) if i != 0 else '', 'index.html'), 'w') as f:
				f.write(template.render(posts = post_list[lower: upper], sitename=self.settings["sitename"]["settings_value"], page_name = "Archive: Post type name"))

	def generate_rss(self, posts, path):
		doc = minidom.Document()
		root_node = doc.createElement('rss')
		
		root_node.setAttribute('xmlns:content','http://purl.org/rss/1.0/modules/content/')
		root_node.setAttribute('xmlns:wfw','http://wellformedweb.org/CommentAPI/')
		root_node.setAttribute('xmlns:dc','http://purl.org/dc/elements/1.1/')
		root_node.setAttribute('xmlns:atom','http://www.w3.org/2005/Atom')
		root_node.setAttribute('xmlns:sy','http://purl.org/rss/1.0/modules/syndication/')
		root_node.setAttribute('xmlns:slash','http://purl.org/rss/1.0/modules/slash/')
		doc.appendChild(root_node)

		channel = doc.createElement("channel")

		title = doc.createElement("title")
		title_text = doc.createTextNode(self.settings["sitename"]["settings_value"])
		title.appendChild(title_text)
		channel.appendChild(title)

		atom_link = doc.createElement("atom:link")
		atom_link.setAttribute('href', self.settings["site_url"]["settings_value"])
		atom_link.setAttribute('rel', 'self')
		atom_link.setAttribute('type', 'application/rss+xml')
		channel.appendChild(atom_link)

		link = doc.createElement('link')
		link_text = doc.createTextNode(self.settings["site_url"]["settings_value"])
		link.appendChild(link_text)
		channel.appendChild(link)

		description = doc.createElement('description')
		description_text = doc.createTextNode(self.settings["site_description"]["settings_value"])
		description.appendChild(description_text)
		channel.appendChild(description)
		#<lastBuildDate>Tue, 27 Aug 2019 07:50:51 +0000</lastBuildDate>
		last_build = doc.createElement('lastBuildDate')
		d = datetime.fromtimestamp(time.time()).astimezone()
		last_build_text = doc.createTextNode(d.strftime('%a, %d %b %Y %H:%M:%S %z'))
		last_build.appendChild(last_build_text)
		channel.appendChild(last_build)
		#<language>en-US</language>
		language = doc.createElement('language')
		language_text = doc.createTextNode('en-US')
		language.appendChild(language_text)
		channel.appendChild(language)
		#<sy:updatePeriod>hourly</sy:updatePeriod>
		update_period = doc.createElement('sy:updatePeriod')
		update_period_text = doc.createTextNode('hourly')
		update_period.appendChild(update_period_text)
		channel.appendChild(update_period)
		#<sy:updateFrequency>1</sy:updateFrequency>
		update_frequency = doc.createElement('sy:updateFrequency')
		update_frequency_text = doc.createTextNode('1')
		update_frequency.appendChild(update_frequency_text)
		channel.appendChild(update_frequency)
		#<generator>https://wordpress.org/?v=5.2.2</generator>
		generator = doc.createElement('generator')
		generator_text = doc.createTextNode('SlothCMS')
		generator.appendChild(generator_text)
		channel.appendChild(generator)

		for post in posts:			
			#<item>
			post_item = doc.createElement('item')
			#	<title>Irregular Batch of Interesting Links #10</title>
			post_title = doc.createElement('title')
			post_title_text = doc.createTextNode(post['title'])
			post_title.appendChild(post_title_text)
			post_item.appendChild(post_title)
			#	<link>https://www.sarahgebauer.com/irregular-batch-of-interesting-links-10/</link>			
			post_link = doc.createElement('link')
			post_link_text = doc.createTextNode(f"{self.settings['site_url']['settings_value']}/{post['post_type_slug']}/{post['title']}")
			post_link.appendChild(post_link_text)
			post_item.appendChild(post_link)
			#	<pubDate>Wed, 28 Aug 2019 07:00:17 +0000</pubDate>
			pub_date = doc.createElement('pubDate')
			d = datetime.fromtimestamp(post['publish_date'] / 1000).astimezone()
			pub_date_text = doc.createTextNode(d.strftime('%a, %d %b %Y %H:%M:%S %z'))
			pub_date.appendChild(pub_date_text)
			post_item.appendChild(pub_date)

			#	<dc:creator><![CDATA[Sarah Gebauer]]></dc:creator>
			#	<category><![CDATA[Interesting links]]></category>
			for category in post['categories']:
				category_node = doc.createElement('category')
				category_text = doc.createCDATASection(category)
				category_node.appendChild(category_text)
				post_item.appendChild(category_node)
			#	<content:encoded><![CDATA[
			content = doc.createElement('content:encoded')
			content_text = doc.createCDATASection(post['content'])
			content.appendChild(content_text)
			post_item.appendChild(content)
			channel.appendChild(post_item)
		root_node.appendChild(channel)

		doc.writexml( open(str(path) + "/feed.xml", 'w'),
               indent="  ",
               addindent="  ",
               newl='\n')

	def generate_home(self):
		# get all post types
		post_type_list = []
		try:
			cur = self.connection.cursor()
			cur.execute(
				sql.SQL("SELECT uuid, slug FROM sloth_post_types")
			)			
			raw_items = cur.fetchall()
			for item in raw_items:
				post_type_list.append({
					"uuid": item[0],
					"slug": item[1]
				})
			cur.close()
		except Exception as e:
			print(371)
			print(e)

		# get 10 latest posts for each post type
		posts = {}
		try:
			cur = self.connection.cursor()
			for post_type in post_type_list:
				cur.execute(
					sql.SQL("SELECT uuid, title, slug, publish_date FROM sloth_posts WHERE post_type = %s AND post_status = %s ORDER BY publish_date DESC LIMIT 10"), [post_type['uuid'], 'published']
				)
				
				raw_items = cur.fetchall()
				temp_list = []
				for item in raw_items:
					temp_list.append({
						"uuid": item[0],
						"title": item[1],
						"slug": item[2],
						"publish_date": item[3]
					})
				posts[post_type['slug']] = temp_list
			cur.close()
		except Exception as e:
			print(390)
			print(e)

		# get template
		home_template_path = Path(self.theme_path, "home.html")
		template = ""
		with open(home_template_path, 'r') as f:
			template = Template(f.read())

		# write file
		home_path_dir = Path(self.config["OUTPUT_PATH"], "index.html")

		with open(home_path_dir, 'w') as f:
			f.write(template.render(posts = posts, sitename=self.settings["sitename"]["settings_value"], page_name = "Home"))

	def regenerate_all(self):
		# get all post types
		# generate all posts
		# generate all categories
		# generate all tags
		# generate all archives
		# generate home

		pass

	def delete_all(self):
		pass
		# get all posts
		# call self.delete_post

	def delete_post(self, post_type_slug, post_slug):
		pass