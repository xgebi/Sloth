import psycopg
from flask import current_app
from pathlib import Path
import os
import threading
import shutil
from typing import Dict, List, Optional
from datetime import datetime
import codecs
from xml.dom import minidom
import time
import math
import traceback
import copy
import html

from app.repositories.post_repositories import get_all_translations
from app.utilities.utilities import get_related_posts
from app.utilities.db_connection import db_connection
from app.toes.markdown_parser import MarkdownParser, combine_footnotes
from app.toes.toes import render_toe_from_string
from app.back_office.post.post_types import PostTypes
from app.toes.hooks import Hooks, Hook
from app.back_office.post.post_query_builder import build_post_query, normalize_post_from_query
from app.services.post_services import get_translations, get_taxonomy_for_post_prepped_for_listing, \
	get_available_translations
import generators


class PostGenerator:
	runnable = True
	theme_path = ""
	menus = {}

	@db_connection
	def __init__(self, *args, connection: psycopg.Connection, **kwargs):
		self.settings = {}
		self.connection = connection
		self.config = current_app.config
		self.menus = self.get_menus()
		# get languages
		self.languages = self.get_languages()
		self.hooks = Hooks()

		# setting global options
		self.set_individual_settings(connection=connection, setting_name='active_theme', settings_type='themes')
		self.set_individual_settings(connection=connection, setting_name='main_language')
		self.set_individual_settings(connection=connection, setting_name='number_rss_posts')
		self.set_individual_settings(connection=connection, setting_name='site_url')
		self.set_individual_settings(connection=connection, setting_name='api_url', alternate_name='sloth_api_url')

		self.set_translatable_individual_settings_by_name(connection=connection, name='sitename')
		self.set_translatable_individual_settings_by_name(connection=connection, name='description')
		self.set_translatable_individual_settings_by_name(connection=connection, name='sub_headline')
		self.set_translatable_individual_settings_by_name(connection=connection, name='archive-title')
		self.set_translatable_individual_settings_by_name(connection=connection, name='category-title')
		self.set_translatable_individual_settings_by_name(connection=connection, name='tag-title')

		# Set path to the theme
		self.theme_path = Path(
			self.config["THEMES_PATH"],
			self.settings['active_theme']['settings_value']
		)

		self.set_footer(connection=connection)

		for language in self.languages:
			if language['uuid'] == self.settings["main_language"]['settings_value']:
				rss_link = f"<link rel=\"alternate\" type=\"application/rss+xml\" title=\"{self.settings['sitename'][language['uuid']]['content']} Feed\" href=\"{self.settings['site_url']['settings_value']}/feed.xml\" />"
			else:
				rss_link = f"<link rel=\"alternate\" type=\"application/rss+xml\" title=\"{self.settings['sitename'][language['uuid']]['content']} Feed\" href=\"{self.settings['site_url']['settings_value']}/{language['short_name']}/feed.xml\" />"
			self.hooks.head.append(Hook(content=rss_link, condition=f"language['uuid'] eq '{language['uuid']}'"))

	def run(
			self,
			*args, post: Dict = {},
			clean_protected=False,
			post_type: str = "",
			everything: bool = True,
			regenerate_taxonomies: List = [],
			multiple: bool = False,
			**kwargs
	):
		""" Main function that runs everything

			Attributes
			----------
			post: str
				Everything regarding a post will be regenerated
			post_type : str
				UUID of a post type, can be empty
			everything : bool
				Tells the function that everything will be regeneratable
		"""
		if not self.runnable or (len(post.keys()) > 0 and len(post_type) > 0):
			return False

		if Path(os.path.join(os.getcwd(), 'generating.lock')).is_file():
			# Queue is on the list of things to be done in foreseeable future
			# return self.add_to_queue(post=post)
			return False

		with open(os.path.join(os.getcwd(), 'generating.lock'), 'w') as f:
			f.write("generation locked")

		if len(post.keys()) > 0 and not clean_protected:
			t = threading.Thread(
				target=self.prepare_single_post,
				kwargs=dict(
					post=post,
					regenerate_taxonomies=regenerate_taxonomies,
					multiple=multiple
				)
			)
		elif len(post.keys()) > 0 and clean_protected:
			t = threading.Thread(
				target=self.prepare_single_post,
				kwargs=dict(
					post=post,
					clean_protected=clean_protected,
					regenerate_taxonomies=regenerate_taxonomies,
					multiple=multiple
				)
			)
		elif len(post_type) > 0:
			t = threading.Thread(
				target=self.generate_post_type,
				kwargs=dict(
					post_type_id=post_type
				)
			)
		elif everything:
			t = threading.Thread(target=self.generate_all)
		else:
			os.remove(Path(os.path.join(os.getcwd(), 'generating.lock')))
			return False
		t.start()
		return True

	def refresh_assets(self):
		if Path(self.config["OUTPUT_PATH"], "assets").is_dir():
			shutil.rmtree(Path(self.config["OUTPUT_PATH"], "assets"))
		if Path(self.config["THEMES_PATH"], self.settings['active_theme']['settings_value'], "assets").is_dir():
			shutil.copytree(Path(self.config["THEMES_PATH"], self.settings['active_theme']['settings_value'], "assets"),
							Path(self.config["OUTPUT_PATH"], "assets"))

	def generate_all(self):
		self.refresh_assets()
		# get post types
		post_types_object = PostTypes()
		post_types = post_types_object.get_post_type_list(self.connection)
		print("languages to be generated")
		# generate posts for languages
		for language in self.languages:
			self.generate_posts_for_language(language=language, post_types=post_types, generate_all=True)
		# remove lock
		os.remove(Path(os.path.join(os.getcwd(), 'generating.lock')))

	def generate_from_post_type_id(self, post_type_id: str, language: Dict[str, str]):
		if language["uuid"] == self.settings["main_language"]['settings_value']:
			# path for main language
			output_path = Path(self.config["OUTPUT_PATH"])
		else:
			# path for other languages
			output_path = Path(self.config["OUTPUT_PATH"], language["short_name"])
			if not output_path.is_dir():
				os.makedirs(output_path)

		self.refresh_assets()

		# get post type
		post_types_object = PostTypes()
		post_type = post_types_object.get_post_type(self.connection, post_type_id=post_type_id)

		self.generate_post_type(post_type, language)

		posts = self.get_posts_from_post_type_language(
			post_type_uuid=post_type['uuid'],
			post_type_slug=post_type['slug'],
			language_uuid=language['uuid']
		)
		self.delete_post_type_post_files(post_type=post_type, language=language)
		self.generate_post_type(posts=posts, output_path=output_path, post_type=post_type, language=language)

		# remove lock
		os.remove(Path(os.path.join(os.getcwd(), 'generating.lock')))

	def generate_post_type(self, posts, output_path, post_type, language):
		self.set_translatable_individual_settings_by_post_type(connection=self.connection, post_type=post_type["uuid"])
		# generate posts
		print("generating posts")
		for post in posts:
			self.generate_post(post=post, language=language, post_type=post_type, output_path=output_path,
							   multiple=True)
		# generate archive and RSS if enabled
		if post_type["archive_enabled"]:
			self.generate_archive(posts=posts, post_type=post_type, output_path=output_path, language=language)
			self.generate_rss(output_path=output_path, posts=posts, post_markdown=True, language=language)

		if post_type["categories_enabled"] or post_type["tags_enabled"]:
			categories, tags = self.prepare_categories_tags_post_type(post_type=post_type, language=language)

		if post_type["categories_enabled"]:
			self.generate_taxonomy(taxonomy=categories, language=language, output_path=output_path,
								   post_type=post_type,
								   title=self.settings["category-title"][language["uuid"]]["content"])

		if post_type["tags_enabled"]:
			self.generate_taxonomy(taxonomy=tags, language=language, output_path=output_path,
								   post_type=post_type, title=self.settings["tag-title"][language["uuid"]]["content"])

	def generate_posts_for_language(self, *args, language: Dict[str, str], post_types: List[Dict[str, str]],
									generate_all=False, **kwargs):
		if language["uuid"] == self.settings["main_language"]['settings_value']:
			# path for main language
			output_path = Path(self.config["OUTPUT_PATH"])
		else:
			# path for other languages
			output_path = Path(self.config["OUTPUT_PATH"], language["short_name"])
			if not output_path.is_dir():
				os.makedirs(output_path)

		for post_type in post_types:
			posts = self.get_posts_from_post_type_language(
				post_type_uuid=post_type['uuid'],
				post_type_slug=post_type['slug'],
				language_uuid=language['uuid']
			)
			self.delete_post_type_post_files(post_type=post_type, language=language)
			print("Deletion successful")
			self.generate_post_type(posts=posts, output_path=output_path, post_type=post_type, language=language)

		# generate home
		self.generate_home(output_path=output_path, post_types=post_types, language=language, generate_all=generate_all)

	def get_posts_for_taxonomy(
			self,
			*args,
			post_type_uuid: str,
			post_type_slug: str,
			taxonomy_uuid: str,
			**kwargs
	):
		try:
			with self.connection.cursor(row_factory=psycopg.rows.dict_row) as cur:
				cur.execute(build_post_query(published_in_taxonomy_per_post_type=True), (taxonomy_uuid, post_type_uuid))
				items = [normalize_post_from_query(post) for post in cur.fetchall()]
		except Exception as e:
			print(e)
			traceback.print_exc()
			return []

		return self.process_posts(items=items, post_type_slug=post_type_slug)

	def get_posts_from_post_type_language(
			self,
			*args,
			post_type_uuid: str,
			language_uuid: str,
			post_type_slug: str,
			**kwargs
	):

		try:
			with self.connection.cursor(row_factory=psycopg.rows.dict_row) as cur:
				cur.execute(build_post_query(published_per_post_type=True), (post_type_uuid, language_uuid))
				items = [normalize_post_from_query(post) for post in cur.fetchall()]
				posts = self.process_posts(items=items, post_type_slug=post_type_slug)
				for post in posts:
					cur.execute(
						"""SELECT sl.location, spl.hook_name
							FROM sloth_post_libraries AS spl
							INNER JOIN sloth_libraries sl on sl.uuid = spl.library
							WHERE spl.post = %s;""",
						(post['uuid'],))
					post["libraries"] = cur.fetchall()
		except Exception as e:
			print(e)
			traceback.print_exc()
			return []

		return posts

	def process_posts(
			self,
			*args,
			items,
			post_type_slug: str,
			**kwargs
	):
		for post in items:
			try:
				thumbnail_path, thumbnail_alt = self.get_thumbnail_information(thumbnail_uuid=post["thumbnail"],
																			   language=post["lang"])
				thumbnail_path = f"/{thumbnail_path}"
				thumbnail_alt = html.escape(thumbnail_alt)

				with self.connection.cursor(row_factory=psycopg.rows.dict_row) as cur:
					if post["original_lang_entry_uuid"]:
						cur.execute(
							"""SELECT lang, slug FROM sloth_posts 
							WHERE uuid = %s OR (original_lang_entry_uuid = %s AND uuid <> %s);""",
							(post["original_lang_entry_uuid"], post["original_lang_entry_uuid"], post["uuid"]))
						language_variants = cur.fetchall()
					else:
						language_variants = []

					cur.execute(
						"""SELECT content, section_type, position
						FROM sloth_post_sections
						WHERE post = %s
						ORDER BY position;""",
						(post["uuid"],))
					sections = [{
						"content": section['content'],
						"type": section['section_type'],
						"position": section['position']
					} for section in cur.fetchall()]
			except Exception as e:
				print(e)
				traceback.print_exc()
				return

			post.update({
				"post_type_slug": post_type_slug,
				"thumbnail_path": thumbnail_path,
				"thumbnail_alt": thumbnail_alt,
				"language_variants": language_variants,
				"meta_description": self.prepare_meta_descriptions(sections=sections, post=post),
				"twitter_description": self.prepare_twitter_descriptions(sections=sections, post=post),
				"sections": sections
			})

		return items

	def prepare_meta_descriptions(self, sections: List, post: Dict) -> str:
		if "meta_description" in post and post["meta_description"] is not None and len(post["meta_description"]) > 0:
			return post["meta_description"]
		if len(sections) > 0:
			return sections[0]["content"][:161 if len(sections[0]) > 161 else len(sections[0]["content"])]
		return ''

	def prepare_twitter_descriptions(self, sections: List, post: Dict) -> str:
		if "twitter_description" in post and post["twitter_description"] is not None and len(
				post["twitter_description"]) > 0:
			return post["twitter_description"]
		if len(sections) > 0:
			return sections[0]["content"][:161 if len(sections[0]) > 161 else len(sections[0]["content"])]
		return ''

	def prepare_single_post(self, *args, post: Dict, regenerate_taxonomies: List, multiple: bool = False,
							clean_protected=False, **kwargs):
		self.clean_taxonomy(taxonomies_for_cleanup=regenerate_taxonomies)
		post_types_object = PostTypes()
		post_types = post_types_object.get_post_type_list(self.connection)
		for pt in post_types:
			if pt['uuid'] == post["post_type"]:
				post_type = pt
				break
		for lang in self.languages:
			if lang['uuid'] == post['lang']:
				language = lang
				break
		if language["uuid"] == self.settings["main_language"]['settings_value']:
			# path for main language
			output_path = Path(self.config["OUTPUT_PATH"])
		else:
			# path for other languages
			output_path = Path(self.config["OUTPUT_PATH"], language["short_name"])
		print(f"output path: {output_path}")

		thumbnail_path, thumbnail_alt = self.get_thumbnail_information(post["thumbnail"], language["uuid"])
		post["thumbnail_path"] = f"/{thumbnail_path}"
		post["thumbnail_alt"] = html.escape(thumbnail_alt)

		if not clean_protected:
			self.generate_post(post=post, language=language, post_type=post_type, output_path=output_path,
							   multiple=multiple)

		if post_type["archive_enabled"]:
			posts = self.get_posts_from_post_type_language(
				post_type_uuid=post_type['uuid'],
				post_type_slug=post_type['slug'],
				language_uuid=language['uuid']
			)
			# generate archive and RSS if enabled
			self.generate_archive(posts=posts, post_type=post_type, output_path=output_path, language=language)
			self.generate_rss(output_path=os.path.join(output_path, post_type['slug']), posts=posts, language=language)

		if post_type["categories_enabled"] or post_type["tags_enabled"]:
			categories, tags = self.prepare_categories_tags(post=post, language=language)

		if post_type["categories_enabled"]:
			self.generate_taxonomy(
				taxonomy=categories,
				language=language,
				output_path=output_path,
				post_type=post_type,
				title=self.settings["category-title"][language["uuid"]]["content"]
			)

		if post_type["tags_enabled"]:
			self.generate_taxonomy(
				taxonomy=tags,
				language=language,
				output_path=output_path,
				post_type=post_type,
				title=self.settings["tag-title"][language["uuid"]]["content"]
			)

		self.generate_home(output_path=output_path, post_types=post_types, language=language)

		if Path(os.path.join(os.getcwd(), 'generating.lock')).is_file():
			os.remove(Path(os.path.join(os.getcwd(), 'generating.lock')))

	def generate_taxonomy(self, *args, taxonomy, language, output_path, post_type, title, **kwargs):
		for item in taxonomy:
			posts = self.get_posts_for_taxonomy(
				post_type_uuid=post_type["uuid"],
				post_type_slug=post_type["slug"],
				taxonomy_uuid=item["uuid"]
			)
			if len(posts) > 0:
				self.generate_archive(
					posts=posts, post_type=post_type, output_path=output_path, language=language, taxonomy=item,
					title=title
				)
				self.generate_rss(
					output_path=os.path.join(output_path, post_type['slug'], item["taxonomy_type"], item["slug"]),
					posts=posts,
					language=language
				)

	def clean_taxonomy(self, *args, taxonomies_for_cleanup: List, **kwargs):
		try:
			with self.connection.cursor(row_factory=psycopg.rows.dict_row) as cur:  # TODO debug this
				for taxonomy in taxonomies_for_cleanup:
					cur.execute(
						"""SELECT st.slug, st.taxonomy_type, sls.uuid, sls.short_name, spt.uuid, spt.slug
							FROM sloth_taxonomy AS st
							INNER JOIN sloth_language_settings AS sls ON st.lang = sls.uuid
							INNER JOIN sloth_post_types spt on st.post_type = spt.uuid
							WHERE st.uuid = %s""",
						(taxonomy["taxonomy"],))
					raw_taxonomy = cur.fetchone()
					taxonomy["slug"] = raw_taxonomy[0]
					taxonomy["type"] = raw_taxonomy[1]
					language = {"short_name": raw_taxonomy[3], "uuid": raw_taxonomy[2]}
					post_type = {"slug": raw_taxonomy[5], "uuid": raw_taxonomy[4]}
					if language["uuid"] == self.settings["main_language"]['settings_value']:
						# path for main language
						posts_path_dir = Path(self.config["OUTPUT_PATH"], post_type["slug"], taxonomy["type"],
											  taxonomy["slug"])
						output_path = Path(self.config["OUTPUT_PATH"])
					else:
						posts_path_dir = Path(self.config["OUTPUT_PATH"], language["short_name"], post_type["slug"],
											  taxonomy["type"], taxonomy["slug"])
						output_path = Path(self.config["OUTPUT_PATH"], language["short_name"])

					if os.path.exists(posts_path_dir):
						shutil.rmtree(posts_path_dir)

					if taxonomy["type"] == "tag":
						title = self.settings["tag-title"][language["uuid"]]["content"]
					elif taxonomy["type"] == "category":
						title = self.settings["category-title"][language["uuid"]]["content"]
					else:
						title = self.settings["archive-title"][language["uuid"]]["content"]
					self.generate_taxonomy(
						taxonomy=(taxonomy,),
						language=language,
						output_path=output_path,
						post_type=post_type,
						title=title
					)
		except Exception as e:
			print(e)
			traceback.print_exc()

	def prepare_categories_tags(self, *args, post: Dict, **kwargs):
		try:
			with self.connection.cursor(row_factory=psycopg.rows.dict_row) as cur:
				cur.execute(
					"""SELECT st.uuid, st.taxonomy_type, st.slug, st.display_name, st.lang
						FROM sloth_post_taxonomies as spt INNER JOIN sloth_taxonomy as st ON spt.taxonomy = st.uuid 
						WHERE spt.post = %s;""",
					(post["uuid"],))
				taxonomies = cur.fetchall()
		except Exception as e:
			print(e)
			traceback.print_exc()

		return self.process_categories_tags(taxonomies=taxonomies)

	def prepare_categories_tags_post_type(self, *args, post_type, language, **kwargs):
		try:
			with self.connection.cursor(row_factory=psycopg.rows.dict_row) as cur:
				cur.execute(
					"""SELECT st.uuid, st.taxonomy_type, st.slug, st.display_name, st.lang
						FROM sloth_taxonomy as st 
						WHERE st.post_type = %s AND st.lang = %s;""",
					(post_type["uuid"], language["uuid"]))
				taxonomies = cur.fetchall()
		except Exception as e:
			print(e)
			traceback.print_exc()

		return self.process_categories_tags(taxonomies=taxonomies) if taxonomies is not None else []

	def process_categories_tags(self, *args, taxonomies: List, **kwargs):
		categories = []
		tags = []
		for taxonomy in taxonomies:
			if taxonomy['taxonomy_type'] == 'category':
				categories.append(taxonomy)
			elif taxonomy['taxonomy_type'] == 'tag':
				tags.append(taxonomy)
		return categories, tags

	def generate_post(
			self,
			*args,
			post: Dict,
			output_path,  # str or Path
			post_type: Dict,
			language: Dict,
			original_post: Optional[Dict] = None,
			multiple: bool = False,
			**kwargs
	):
		print("generating single post")
		for lib in post["libraries"]:
			script = f"<script src=\"{lib['location']}\" async></script>"
			if lib["hook_name"] == "head":
				self.hooks.head.append(Hook(content=script, condition=f"post['uuid'] eq '{post['uuid']}'"))
			elif lib["hook_name"] == "footer":
				self.hooks.footer.append(Hook(content=script, condition=f"post['uuid'] eq '{post['uuid']}'"))

		post_path_dir = Path(output_path, post_type["slug"], post["slug"])

		template = self.get_post_template(post_type=post_type, post=post, language=language)

		if not os.path.exists(post_path_dir):
			os.makedirs(post_path_dir)

		with self.connection.cursor(row_factory=psycopg.rows.dict_row) as cur:
			translations_temp = get_available_translations(connection=self.connection, languages=self.languages, post_uuid=post['original_lang_entry_uuid'] if 'original_lang_entry_uuid' in post and post['original_lang_entry_uuid'] is not None and len(post['original_lang_entry_uuid']) > 0 else post['uuid'])

		translations_filtered = [translation for translation in translations_temp if
								 translation["status"].lower() == 'published' and translation['post_uuid'] != post['uuid'] ]

		translations = self.get_translation_links(translations=translations_filtered, post_type=post_type, post=post)

		categories, tags = get_taxonomy_for_post_prepped_for_listing(
			connection=self.connection,
			uuid=post['uuid'],
			main_language=self.settings['main_language'],
			language=language,
			post_type_slug=post_type["slug"]
		)
		print(post["title"])
		print("pre write")
		with codecs.open(os.path.join(post_path_dir, 'index.html'), "w", "utf-8") as f:
			md_parser = MarkdownParser()
			i = 0
			content_with_forms = ""
			excerpt_with_forms = ""
			partial_content_footnotes = ""
			add_content_form_hooks = False
			content_footnotes = []
			for section in post["sections"]:
				if i == 0:
					if section["type"] == "form":
						excerpt_with_forms = ""
						content_with_forms += self.get_form(section["content"])
						add_content_form_hooks = True
						i += 2
					else:
						excerpt_with_forms = copy.deepcopy(section["content"])
						i += 1
				else:
					if section["type"] == "form":
						add_content_form_hooks = True
						partial_content_with_forms = self.get_form(section["content"])
					else:
						partial_content_with_forms = copy.deepcopy(section["content"])
						partial_content_with_forms, partial_content_footnotes = md_parser.to_html_string(
							partial_content_with_forms)
					content_with_forms += partial_content_with_forms
					content_footnotes.extend(partial_content_footnotes)

			if add_content_form_hooks:
				post["has_form"] = True
				with open(Path(__file__).parent / "../../templates/send-message.toe.html", 'r', encoding="utf-8") as fi:
					self.hooks.footer.append(Hook(content=fi.read(), condition="post['has_form']"))
			else:
				post["has_form"] = False

			post["excerpt"], excerpt_footnotes = md_parser.to_html_string(excerpt_with_forms)
			excerpt_footnotes.extend(content_footnotes)
			post["content"] = combine_footnotes(text=content_with_forms, footnotes=excerpt_footnotes)

			rendered = render_toe_from_string(
				template=template,
				data={
					"post": post,
					"sitename": self.settings["sitename"][language["uuid"]]["content"],
					"sloth_api_url": self.settings["sloth_api_url"]["settings_value"],
					"site_url": self.settings["site_url"]["settings_value"],
					"post_url": f"{self.settings['site_url']['settings_value']}/{post_type['slug']}/{post['slug']}",
					"menus": self.menus,
					"translations": translations,
					"is_home": False,
					"is_post": True,
					"language": language["uuid"],
					"categories": categories,
					"tags": tags,
				},
				hooks=self.hooks,
				base_path=self.theme_path
			)
			f.write(rendered)
		print("fuck yeah")
		if post["js"] and len(post["js"]) > 0:
			with open(os.path.join(post_path_dir, 'script.js'), 'w', encoding="utf-8") as f:
				f.write(post["js"])
		elif (Path(os.path.join(post_path_dir, 'script.js'))).is_file():
			os.remove(Path(os.path.join(post_path_dir, 'script.js')))

		if post["css"] and len(post["css"]) > 0:
			with open(os.path.join(post_path_dir, 'style.css'), 'w', encoding="utf-8") as f:
				f.write(post["css"])
		elif (Path(os.path.join(post_path_dir, 'style.css'))).is_file():
			os.remove(Path(os.path.join(post_path_dir, 'style.css')))

		if "related_posts" in post and original_post is None and not multiple:
			post["related_posts"] = [post for post in post["related_posts"] if post['post_status'] == 'published']
			for related_post in post["related_posts"]:
				for lang in self.languages:
					if lang['uuid'] == related_post['lang']:
						if lang['uuid'] == self.settings["main_language"]['settings_value']:
							loc_output_path = Path(self.config["OUTPUT_PATH"])
						else:
							short_name = ""
							for translation in translations_filtered:
								if translation["lang_uuid"] == related_post["lang"]:
									short_name = translation["short_name"]

							loc_output_path = Path(self.config["OUTPUT_PATH"], short_name)
						self.generate_post(
							post=related_post,
							output_path=loc_output_path,
							post_type=post_type,
							language=lang,
							original_post=post,
							multiple=multiple
						)
						break

	def get_thumbnail_information(self, thumbnail_uuid: str, language: str) -> (str, str):
		if thumbnail_uuid is None:
			return "", ""
		try:
			with self.connection.cursor() as cur:  # Here the empty arguments make sense
				cur.execute("""SELECT sm.file_path, sma.alt FROM sloth_media as sm
                    INNER JOIN sloth_media_alts as sma on sm.uuid = sma.media
                    WHERE sm.uuid = %s AND sma.lang = %s;""",
							(thumbnail_uuid, language))
				return cur.fetchone()
		except Exception as e:
			print(e)
			traceback.print_exc()
		return "", ""

	def get_post_template(self, *args, post_type: Dict, post: Dict, language: Dict, **kwargs) -> Optional[str]:
		# post type, post format, language
		if os.path.isfile(os.path.join(self.theme_path,
									   f"post-{post_type['slug']}-{post['post_format_slug']}-{language['short_name']}.toe.html")):
			post_template_path = os.path.join(self.theme_path,
											  f"post-{post_type['slug']}-{post['post_format_slug']}-{language['short_name']}.toe.html")
		# post type, post format
		elif os.path.isfile(
				os.path.join(self.theme_path, f"post-{post_type['slug']}-{post['post_format_slug']}.toe.html")):
			post_template_path = os.path.join(self.theme_path,
											  f"post-{post_type['slug']}-{post['post_format_slug']}.toe.html")
		# post format, language
		elif os.path.isfile(
				os.path.join(self.theme_path, f"post-{post['post_format_slug']}-{language['short_name']}.toe.html")):
			post_template_path = os.path.join(self.theme_path,
											  f"post-{post['post_format_slug']}-{language['short_name']}.toe.html")
		# post type, language
		elif os.path.isfile(
				os.path.join(self.theme_path, f"post-{post_type['slug']}-{language['short_name']}.toe.html")):
			post_template_path = os.path.join(self.theme_path,
											  f"post-{post_type['slug']}-{language['short_name']}.toe.html")
		# post type
		elif os.path.isfile(os.path.join(self.theme_path, f"post-{post_type['slug']}.toe.html")):
			post_template_path = os.path.join(self.theme_path,
											  f"post-{post_type['slug']}.toe.html")
		# language
		elif os.path.isfile(os.path.join(self.theme_path, f"post-{language['short_name']}.toe.html")):
			post_template_path = os.path.join(self.theme_path,
											  f"post-{language['short_name']}.toe.html")
		# post format
		elif os.path.isfile(os.path.join(self.theme_path, f"post-{post['post_format_slug']}.toe.html")):
			post_template_path = os.path.join(self.theme_path,
											  f"post-{post['post_format_slug']}.toe.html")
		else:
			post_template_path = Path(self.theme_path, "post.toe.html")

		with open(post_template_path, 'r', encoding="utf-8") as f:
			return f.read()

	def get_translation_links(self, *args, translations: List, post_type: Dict, post: Dict, **kwargs):
		# {'uuid': '48ab80ef-b83b-40f7-9dab-c3343bae7d0e', 'long_name': 'English', 'short_name': 'en', 'post': 'fb2e1b26-3361-4239-9b97-aedcde0f57cf'}
		# /<short_name>/<post_type_slug>/<post_slug>
		result = []

		for translation in translations:
			if post['lang'] != translation['lang_uuid']:
				if translation["lang_uuid"] != self.settings["main_language"]['settings_value']:
					result.append({
						"lang_uuid": translation['lang_uuid'],
						"post_uuid": translation['post_uuid'],
						"language": translation['long_name'],
						"link": f"/{translation['short_name']}/{post_type['slug']}/{translation['slug']}"
					})
				else:
					result.append({
						"lang_uuid": translation['lang_uuid'],
						"post_uuid": translation['post_uuid'],
						"language": translation['long_name'],
						"link": f"/{post_type['slug']}/{translation['slug']}"
					})
		return result

	def generate_archive(self, *args, posts, output_path, post_type, language, taxonomy=None, title="", **kwargs):
		if len(posts) == 0:
			return

		# TODO good enough for now
		for post in posts:
			categories, tags = get_taxonomy_for_post_prepped_for_listing(
				connection=self.connection,
				uuid=post['uuid'],
				main_language=self.settings['main_language'],
				language=language,
				post_type_slug=post_type['slug']
			)
			post.update({
				"categories": categories,
				"tags": tags,
				"post_type_slug": post_type['slug'],
			})

		if taxonomy:
			archive_path_dir = Path(output_path, post_type["slug"], taxonomy["taxonomy_type"], taxonomy["slug"])
		else:
			archive_path_dir = Path(output_path, post_type["slug"])

		if os.path.isfile(
				os.path.join(self.theme_path, f"archive-{post_type['slug']}-{language['short_name']}.toe.html")):
			archive_template_path = os.path.join(self.theme_path,
												 f"archive-{post_type['slug']}-{language['short_name']}.toe.html")
		elif os.path.isfile(os.path.join(self.theme_path, f"archive-{post_type['slug']}.toe.html")):
			archive_template_path = os.path.join(self.theme_path,
												 f"archive-{post_type['slug']}.toe.html")
		elif os.path.isfile(os.path.join(self.theme_path, f"archive-{language['short_name']}.toe.html")):
			archive_template_path = os.path.join(self.theme_path,
												 f"archive-{language['short_name']}.toe.html")
		else:
			archive_template_path = Path(self.theme_path, "archive.toe.html")

		with open(archive_template_path, 'r', encoding="utf-8") as f:
			template = f.read()

		if not os.path.exists(archive_path_dir):
			os.makedirs(archive_path_dir)

		for i in range(math.ceil(len(posts) / 10)):
			if i > 0 and not os.path.exists(os.path.join(archive_path_dir, str(i))):
				os.makedirs(os.path.join(archive_path_dir, str(i)))

			path_to_index = os.path.join(archive_path_dir, str(i), 'index.html')
			if i == 0:
				path_to_index = os.path.join(archive_path_dir, 'index.html')

			with open(path_to_index, 'w', encoding="utf-8") as f:
				lower = 10 * i
				upper = (10 * i) + 10 if (10 * i) + 10 < len(posts) else len(
					posts)

				f.write(
					render_toe_from_string(
						base_path=self.theme_path,
						template=template,
						data={
							"posts": posts[lower: upper],
							"sitename": self.settings["sitename"][language["uuid"]]["content"],
							"title": self.settings["archive-title"][language["uuid"]]["content"] if len(
								title) == 0 else title,
							"site_url": self.settings["site_url"]["settings_value"],
							"page_name": f"{self.settings['archive-title'][language['uuid']]['content']} {post_type['display_name']}",
							"post_type": post_type,
							"sloth_api_url": self.settings["sloth_api_url"]["settings_value"],
							"menus": self.menus,
							"current_page_number": i,
							"number_of_pages": math.ceil(len(posts) / 10),
							"not_last_page": True if math.floor(len(posts) / 10) != i else False,
							"is_home": False,
							"is_post": False,
							"language": language["uuid"]
						},
						hooks=self.hooks
					))

	def get_menus(self, *args, **kwargs):
		menus = {}
		try:
			with self.connection.cursor(row_factory=psycopg.rows.dict_row) as cur:
				cur.execute("""SELECT name, uuid FROM sloth_menus;""")
				menus = {menu['name']: {"items": [], "uuid": menu['uuid'], "name": menu['name']} for menu in
						 cur.fetchall()}
				for menu in menus.keys():
					cur.execute("""SELECT title, url FROM sloth_menu_items WHERE menu = %s""",
								(menus[menu]["uuid"],)
								)
					menus[menu]["items"] = cur.fetchall()
		except Exception as e:
			print(f"PostGenerator.get_menus {e}")
			traceback.print_exc()

		return menus

	def get_protected_post(self, *args, uuid: str, **kwargs):
		try:
			with self.connection.cursor(row_factory=psycopg.rows.dict_row) as cur:
				# This is a rudimentary version
				cur.execute("""SELECT title, thumbnail, lang 
                    FROM sloth_posts WHERE uuid = %s;""",
							(uuid,))
				post = cur.fetchone()
				cur.execute(
					"""SELECT content FROM sloth_post_sections WHERE post = %s AND section_type = 'text' ORDER BY position;""",
					(uuid,))
				sections = cur.fetchall()

				md_parser = MarkdownParser()
				post["full_content"] = ""

				for section in sections:
					post["full_content"] += generators.rust_generators.render_slothmark(section['content'])

				if post['thumbnail'] is not None:
					cur.execute("""SELECT sm.file_path, sma.alt 
                                    FROM sloth_media AS sm
                                     INNER JOIN sloth_media_alts sma on sm.uuid = sma.uuid
                                     WHERE sm.uuid = %s and sma.lang = %s;""",
								(post['thumbnail'], post['lang']))
					raw_thumbnail = cur.fetchone()
					post["thumbnail"] = raw_thumbnail['file_path']
					post["thumbnail_alt"] = raw_thumbnail['alt']
		except Exception as e:
			print(e)
			traceback.print_exc()

		if os.path.isfile(os.path.join(self.theme_path, "secret.toe.html")):
			with open(os.path.join(self.theme_path, "secret.toe.html"), 'r', encoding="utf-8") as f:
				protected_template = f.read()
				return protected_template.render(post=post)  # TODO redo this

		else:
			return post

	def set_footer(self, *args, **kwargs):
		# Footer for post
		with open(Path(__file__).parent / "../../templates/analytics.toe.html", 'r', encoding="utf-8") as f:
			self.hooks.footer.append(Hook(content=f.read()))

		with open(Path(__file__).parent / "../../templates/secret-script.toe.html", 'r', encoding="utf-8") as f:
			self.hooks.footer.append(Hook(content=f.read(), condition="is_home"))

	def set_translatable_individual_settings_by_name(
			self,
			*args,
			connection: psycopg.Connection,
			name: str,
			**kwargs):
		try:
			with connection.cursor(row_factory=psycopg.rows.dict_row) as cur:
				cur.execute("""SELECT uuid, name, content, lang 
                    FROM sloth_localized_strings WHERE name = %s;""",
							(name,))
				raw_items = cur.fetchall()
		except Exception as e:
			print(e)
			traceback.print_exc()

		for item in raw_items:
			if name not in self.settings:
				self.settings[name] = {
					item['lang']: {
						"uuid": item['uuid'],
						"content": item['content']
					}
				}
			else:
				self.settings[name][item['lang']] = {
					"uuid": item['uuid'],
					"content": item['content']
				}

	def set_translatable_individual_settings_by_post_type(
			self,
			*args,
			connection: psycopg.Connection,
			post_type: str,
			**kwargs):
		try:
			with connection.cursor(row_factory=psycopg.rows.dict_row) as cur:
				cur.execute("""SELECT uuid, name, content, lang, post_type 
                    FROM sloth_localized_strings WHERE post_type = %s;""",
							(post_type,))
				raw_items = cur.fetchall()
				for item in raw_items:
					if post_type not in self.settings:
						self.settings[post_type] = {
							item['lang']: {
								"uuid": item['uuid'],
								"content": item['content']
							}
						}
					else:
						self.settings[post_type][item['lang']] = {
							"uuid": item['uuid'],
							"content": item['content']
						}
		except Exception as e:
			print(e)
			traceback.print_exc()

	def set_individual_settings(self, *args, connection: psycopg.Connection, setting_name: str,
								alternate_name: str = None, settings_type: str = 'sloth', **kwargs):
		try:
			with connection.cursor(row_factory=psycopg.rows.dict_row) as cur:
				cur.execute("""SELECT settings_name, settings_value, settings_value_type 
                                    FROM sloth_settings WHERE settings_name = %s AND settings_type = %s""",
							(setting_name, settings_type))
				items = cur.fetchall()
		except Exception as e:
			print(e)
			traceback.print_exc()

		if alternate_name is None:
			for item in items:
				self.settings[str(item['settings_name'])] = {
					"settings_name": item['settings_name'],
					"settings_value": item['settings_value'],
					"settings_value_type": item['settings_value_type']
				}
		else:
			for item in items:
				self.settings[alternate_name] = {
					"settings_name": item['settings_name'],
					"settings_value": item['settings_value'],
					"settings_value_type": item['settings_value_type']
				}

	def get_languages(self):
		languages = []
		try:
			with self.connection.cursor(row_factory=psycopg.rows.dict_row) as cur:
				cur.execute("""SELECT uuid, long_name, short_name FROM sloth_language_settings""")
				languages = cur.fetchall()
		except Exception as e:
			print(e)
			traceback.print_exc()

		return languages

	def get_form(self, name: str):
		# get form
		form = []
		try:
			with self.connection.cursor(row_factory=psycopg.rows.dict_row) as cur:
				cur.execute("""SELECT sff.uuid, sff.name, sff.position, sff.is_childless, sff.type, 
                    sff.is_required, sff.label FROM sloth_form_fields AS sff
                    INNER JOIN sloth_forms AS sf ON sff.form = sf.uuid
                    WHERE sf.name = %s ORDER BY sff.position;""",
							(name,))
				rows = cur.fetchall()
				for row in rows:
					form.append(row)
		except Exception as e:
			print(e)
			traceback.print_exc()
			return

		# build form
		form_text = f"<form class='sloth-form' data-form=\"{name[len('<(form'):-2].strip()}\">"
		for field in form:
			form_text += f"<div><label for=\"{field['name']}\">"
			is_required = ""
			if field['is_required']:
				is_required = "required"
			if field['type'] == "submit":
				form_text += f"<input type='submit' value='{field['label']}' />"
			elif field['type'] == "checkbox":
				form_text += f"<input type='checkbox' name='{field['name']}' id='{field['name']}' {is_required} /> {field['label']}</label>"
			else:
				form_text += f"{field['label']}</label><br />"
				if field['type'] == 'textarea':
					form_text += f"<textarea name='{field['name']}' id='{field['name']}' {is_required}></textarea>"
				elif field['type'] == 'select':
					form_text += f"<select name='{field['name']}' id='{field['name']}' {is_required}></select>"
				else:
					form_text += f"<input type='{field['type']}' name='{field['name']}' id='{field['name']}' {is_required} />"
			form_text += "</div>"
		form_text += f"<input type='text' style='display: none' name='spam-catcher' class='spam-catcher' />"
		form_text += "</form>"

		return form_text

	# delete post files
	def delete_post_files(self, *args, post_type: Dict, post: Dict, language: Dict, **kwargs):
		if language["uuid"] == self.settings["main_language"]['settings_value']:
			# path for main language
			post_path_dir = Path(self.config["OUTPUT_PATH"], post_type['slug'], post["slug"])
		else:
			# path for other languages
			post_path_dir = Path(self.config["OUTPUT_PATH"], language["short_name"], post_type['slug'], post["slug"])

		if os.path.exists(post_path_dir):
			shutil.rmtree(post_path_dir)

	# delete post type files
	def delete_post_type_post_files(self, *args, post_type: Dict, language: Dict, **kwargs):
		if language["uuid"] == self.settings["main_language"]['settings_value']:
			# path for main language
			posts_path_dir = Path(self.config["OUTPUT_PATH"], post_type["slug"])
		else:
			# path for other languages
			posts_path_dir = Path(self.config["OUTPUT_PATH"], language["short_name"], post_type["slug"])

		if os.path.exists(posts_path_dir):
			shutil.rmtree(posts_path_dir)

	def generate_home(
			self,
			*args,
			output_path: Path,
			post_types: List[Dict[str, str]],
			language: Dict,
			generate_all=False,
			**kwargs
	):
		self.generate_rss(posts=self.prepare_rss_home_data(language=language), output_path=output_path,
						  language=language)
		if (generate_all and self.config["OUTPUT_PATH"] == str(output_path)) or not generate_all:
			self.generate_sitemap()
		posts = {}
		try:
			with self.connection.cursor(row_factory=psycopg.rows.dict_row) as cur:
				for post_type in post_types:
					cur.execute(
						"""SELECT sp.uuid, sp.title, sp.slug, 
							(SELECT content FROM sloth_post_sections as sps WHERE sps.position = 0 AND sps.post = sp.uuid) as content, 
							sp.publish_date, sp.thumbnail, sp.pinned
							FROM sloth_posts AS sp
							WHERE post_type = %s AND post_status = 'published' AND lang = %s AND pinned = %s
							ORDER BY publish_date DESC LIMIT %s""",
						(post_type['uuid'], language['uuid'], True,
						 int(self.settings['number_rss_posts']['settings_value'])))
					items = cur.fetchall()
					if int(self.settings['number_rss_posts']['settings_value']) - len(items) > 0:
						# TODO debug this
						cur.execute(
							"""SELECT sp.uuid, sp.title, sp.slug, 
								(SELECT content FROM sloth_post_sections as sps WHERE sps.position = 0 AND sps.post = sp.uuid) as content, 
								sp.publish_date, sp.thumbnail, sp.pinned 
								FROM sloth_posts AS sp
									WHERE post_type = %s AND post_status = 'published' AND lang = %s  AND pinned = %s
									ORDER BY publish_date DESC LIMIT %s""",
							(post_type['uuid'], language['uuid'], False,
							 int(self.settings['number_rss_posts']['settings_value']) - len(items)))
						items.extend(cur.fetchall())
					md_parser = MarkdownParser()
					posts[post_type['slug']] = []

					for item in items:
						thumbnail_alt = None
						thumbnail_path = None
						if item['thumbnail'] is not None:
							cur.execute("""SELECT file_path, alt FROM sloth_media as sm
                                            INNER JOIN sloth_media_alts AS sma ON sma.media = sm.uuid
                                            WHERE sma.lang = %s AND sm.uuid = %s;""",
										(language['uuid'], item['thumbnail']))
							res = cur.fetchone()
							thumbnail_path = f"/{res['file_path']}"
							thumbnail_alt = res['alt']
						excerpt, excerpt_footnotes = md_parser.to_html_string(item['content'])

						categories, tags = get_taxonomy_for_post_prepped_for_listing(
							connection=self.connection,
							uuid=item['uuid'],
							main_language=self.settings['main_language'],
							language=language,
							post_type_slug=post_type['slug']
						)
						classes = " ".join(
							[f"category-{category['slug']}" for category in categories] + [f"tag-{tag['slug']}" for tag
																						   in tags])
						if item['pinned']:
							classes += " pinned"
							classes = classes.strip()
						item.update({
							"excerpt": excerpt,
							"publish_timedate_formatted": datetime.fromtimestamp(
								float(item['publish_date']) / 1000).strftime(
								"%Y-%m-%d %H:%M"),
							"post_type_slug": post_type['slug'],
							"thumbnail_path": thumbnail_path,
							"thumbnail_alt": thumbnail_alt,
							"classes": classes,
							"categories": categories,
							"tags": tags
						})
						posts[post_type['slug']].append(item)
		except Exception as e:
			print(390)
			print(e)
			traceback.print_exc()

		# get template
		home_template_path = Path(self.theme_path, f"home-{language['short_name']}.toe.html")
		if not home_template_path.is_file():
			home_template_path = Path(self.theme_path, f"home.toe.html")

		with open(home_template_path, 'r', encoding="utf-8") as f:
			template = f.read()

		# write file
		home_path_dir = os.path.join(output_path, "index.html")

		with open(home_path_dir, 'w', encoding="utf-8") as f:
			f.write(render_toe_from_string(
				base_path=self.theme_path,
				template=template,
				data={
					"posts": posts,
					"sitename": self.settings["sitename"][language["uuid"]]["content"],
					"description": self.settings["description"][language["uuid"]]["content"],
					"page_name": "Home",
					"sloth_api_url": self.settings["sloth_api_url"]["settings_value"],
					"site_url": self.settings["site_url"]["settings_value"],
					"menus": self.menus,
					"is_home": True,
					"is_post": False,
					"language": language["uuid"]
				},
				hooks=self.hooks
			))

	def prepare_rss_home_data(self, *args, language: Dict, **kwargs):
		try:
			with self.connection.cursor(row_factory=psycopg.rows.dict_row) as cur:
				cur.execute("""SELECT A.uuid, A.slug, B.display_name, B.uuid, A.title, A.css, 
                             A.js, A.use_theme_css, A.use_theme_js,
                        A.publish_date, A.update_date, A.post_status, C.slug as post_type_slug, C.uuid as post_type_uuid
                                    FROM sloth_posts AS A INNER JOIN sloth_users AS B ON A.author = B.uuid 
                                    INNER JOIN sloth_post_types AS C ON A.post_type = C.uuid
                                    WHERE C.archive_enabled = %s AND A.post_status = 'published' AND A.lang = %s
                                    ORDER BY A.publish_date DESC LIMIT %s""",
							(True, language['uuid'], int(self.settings['number_rss_posts']['settings_value'])))
				posts = cur.fetchall()

				for post in posts:
					post.update({
						"publish_timedate_formatted": datetime.fromtimestamp(float(post['publish_date']) / 1000).strftime(
							"%Y-%m-%d %H:%M"),
						"update_date_formatted": datetime.fromtimestamp(float(post['update_date']) / 1000).strftime("%Y-%m-%d %H:%M"),
					})

					cur.execute(
						"""SELECT content, section_type, position
							FROM sloth_post_sections
							WHERE post = %s
							ORDER BY position ASC;""",
						(post["uuid"],))
					sections = cur.fetchall()

					post["excerpt"] = sections[0]["content"] if len(sections) > 0 else ""
					post["content"] = "\n".join([section["content"] for section in sections if
												 section["position"] > 0 and section["content"] is not None])

		except Exception as e:
			print(371)
			print(e)
			traceback.print_exc()

		return posts

	def generate_rss(self, *args, output_path: bytes, posts: List, language: Dict, post_markdown: bool = False,
					 **kwargs):
		doc = minidom.Document()
		root_node = doc.createElement('rss')

		root_node.setAttribute('version', '2.0')
		root_node.setAttribute('xmlns:content', 'http://purl.org/rss/1.0/modules/content/')
		root_node.setAttribute('xmlns:wfw', 'http://wellformedweb.org/CommentAPI/')
		root_node.setAttribute('xmlns:dc', 'http://purl.org/dc/elements/1.1/')
		root_node.setAttribute('xmlns:atom', 'http://www.w3.org/2005/Atom')
		root_node.setAttribute('xmlns:sy', 'http://purl.org/rss/1.0/modules/syndication/')
		root_node.setAttribute('xmlns:slash', 'http://purl.org/rss/1.0/modules/slash/')
		doc.appendChild(root_node)

		channel = doc.createElement("channel")

		title = doc.createElement("title")
		title_text = doc.createTextNode(self.settings["sitename"][language["uuid"]]["content"])
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

		description_text = doc.createTextNode(self.settings["description"][language["uuid"]]["content"])
		description.appendChild(description_text)
		channel.appendChild(description)
		# <lastBuildDate>Tue, 27 Aug 2019 07:50:51 +0000</lastBuildDate>
		last_build = doc.createElement('lastBuildDate')
		d = datetime.fromtimestamp(time.time()).astimezone()
		last_build_text = doc.createTextNode(d.strftime('%a, %d %b %Y %H:%M:%S %z'))
		last_build.appendChild(last_build_text)
		channel.appendChild(last_build)
		# <language>en-US</language>
		language = doc.createElement('language')
		language_text = doc.createTextNode('en-US')
		language.appendChild(language_text)
		channel.appendChild(language)
		# <sy:updatePeriod>hourly</sy:updatePeriod>
		update_period = doc.createElement('sy:updatePeriod')
		update_period_text = doc.createTextNode('hourly')
		update_period.appendChild(update_period_text)
		channel.appendChild(update_period)
		# <sy:updateFrequency>1</sy:updateFrequency>
		update_frequency = doc.createElement('sy:updateFrequency')
		update_frequency_text = doc.createTextNode('1')
		update_frequency.appendChild(update_frequency_text)
		channel.appendChild(update_frequency)
		# <generator>https://wordpress.org/?v=5.2.2</generator>
		generator = doc.createElement('generator')
		generator_text = doc.createTextNode('SlothCMS')
		generator.appendChild(generator_text)
		channel.appendChild(generator)

		for post in posts:
			# <item>
			post_item = doc.createElement('item')
			# <title>Irregular Batch of Interesting Links #10</title>
			post_title = doc.createElement('title')
			post_title_text = doc.createTextNode(post['title'])
			post_title.appendChild(post_title_text)
			post_item.appendChild(post_title)
			# <link>https://www.sarahgebauer.com/irregular-batch-of-interesting-links-10/</link>
			post_link = doc.createElement('link')

			post_link_text = doc.createTextNode(
				f"{self.settings['site_url']['settings_value']}/{post['post_type_slug']}/{post['slug']}")
			post_link.appendChild(post_link_text)
			post_item.appendChild(post_link)
			guid = doc.createElement("guid")
			guid.appendChild(doc.createTextNode(
				f"{self.settings['site_url']['settings_value']}/{post['post_type_slug']}/{post['slug']}"))
			post_item.appendChild(guid)
			# <pubDate>Wed, 28 Aug 2019 07:00:17 +0000</pubDate>
			pub_date = doc.createElement('pubDate')
			d = datetime.fromtimestamp(post['publish_date'] / 1000).astimezone()
			pub_date_text = doc.createTextNode(d.strftime('%a, %d %b %Y %H:%M:%S %z'))
			pub_date.appendChild(pub_date_text)
			post_item.appendChild(pub_date)

			# <dc:creator><![CDATA[Sarah Gebauer]]></dc:creator>
			# <category><![CDATA[Interesting links]]></category>
			# if isinstance(post['categories'], collections.Iterable):
			#    for category in post['categories']:
			#        category_node = doc.createElement('category')
			#        category_text = doc.createCDATASection(category["display_name"])
			#        category_node.appendChild(category_text)
			#        post_item.appendChild(category_node)
			# <content:encoded><![CDATA[
			description = doc.createElement('description')
			post_item.appendChild(description)

			content = doc.createElement('content:encoded')
			md_parser = MarkdownParser()
			content_text = doc.createCDATASection("")
			if "sections" in post:
				if not post_markdown:
					footnotes = []
					sections = []
					for section in post["sections"]:
						temp_text, temp_footnotes = md_parser.to_html_string(section["content"])
						footnotes.extend(temp_footnotes)
						sections.append(temp_text)
					content_text = doc.createCDATASection(
						combine_footnotes(text="\n".join(sections), footnotes=footnotes)
					)
				else:
					content_text = doc.createCDATASection(
						"\n".join([section["content"] for section in post["sections"]])
					)
			elif "content" in post or "excerpt" in post:
				if len(post["excerpt"]) == 0:
					post["content"], footnotes = md_parser.to_html_string(post["content"])
					content_text = doc.createCDATASection(combine_footnotes(text=post['content'], footnotes=footnotes))
				else:
					post["excerpt"], ex_footnotes = md_parser.to_html_string(post["excerpt"])
					post["content"], con_footnotes = md_parser.to_html_string(post["content"])
					content_text = doc.createCDATASection(combine_footnotes(text=f"{post['excerpt']} {post['content']}",
																			footnotes=ex_footnotes.extend(
																				con_footnotes)))
			content.appendChild(content_text)
			post_item.appendChild(content)
			channel.appendChild(post_item)
		root_node.appendChild(channel)

		with codecs.open(os.path.join(output_path, "feed.xml"), "w", "utf-8") as f:
			f.write(doc.toprettyxml())

	def generate_sitemap(self, *args, **kwargs):
		# <?xml version="1.0" encoding="UTF-8"?>
		# <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
		# <url><loc>http://www.example.com/index.html</loc></url>
		# </urlset>

		# self.settings['site_url']['settings_value']

		output_path = self.config["OUTPUT_PATH"]

		doc = minidom.Document()
		root_node = doc.createElement('urlset')
		root_node.setAttribute('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
		doc.appendChild(root_node)

		try:
			with self.connection.cursor(row_factory=psycopg.rows.dict_row) as cur:
				# Get languages
				cur.execute("""SELECT settings_value FROM sloth_settings WHERE settings_name = 'main_language';""")
				main_lang = cur.fetchone()['settings_value']
				cur.execute("""SELECT uuid, short_name FROM sloth_language_settings;""")
				result = cur.fetchall()

				langs = {lang['uuid']: {
					"uuid": lang['uuid'],
					"path": f"{lang['short_name']}" if lang['uuid'] != main_lang else "",
				} for lang in result}

				#   Get post types
				cur.execute("""SELECT uuid, slug FROM sloth_post_types;""")
				post_type_slugs = {slug['uuid']: {
					"slug": slug['slug']
				} for slug in cur.fetchall()}

				for lang in langs.keys():
					home_url = doc.createElement("url")
					home_loc = doc.createElement("loc")
					home_loc.appendChild(
						doc.createTextNode(f"{self.settings['site_url']['settings_value']}/{langs[lang]['path']}"))
					home_url.appendChild(home_loc)
					home_change_freq = doc.createElement("changefreq")
					home_change_freq.appendChild(doc.createTextNode("daily"))
					home_url.appendChild(home_change_freq)
					home_last_mod = doc.createElement("lastmod")
					home_last_mod.appendChild(doc.createTextNode(datetime.now().strftime("%Y-%m-%d")))
					home_url.appendChild(home_last_mod)
					root_node.appendChild(home_url)

					for post_type in post_type_slugs.keys():
						if not Path(output_path, langs[lang]['path'], post_type_slugs[post_type]['slug']).is_dir():
							continue
						pt_url = doc.createElement("url")
						pt_loc = doc.createElement("loc")
						if len(langs[lang]['path']) == 0:
							pt_loc.appendChild(
								doc.createTextNode(
									f"{self.settings['site_url']['settings_value']}/{post_type_slugs[post_type]['slug']}"))
						else:
							pt_loc.appendChild(
								doc.createTextNode(
									f"{self.settings['site_url']['settings_value']}/{langs[lang]['path']}/{post_type_slugs[post_type]['slug']}"))
						pt_url.appendChild(pt_loc)
						pt_change_freq = doc.createElement("changefreq")
						pt_change_freq.appendChild(doc.createTextNode("weekly"))
						pt_url.appendChild(pt_change_freq)
						root_node.appendChild(pt_url)

						# get categories per post type
						cur.execute("""SELECT slug FROM sloth_taxonomy 
                            WHERE taxonomy_type = %s AND post_type = %s;""",
									('category', post_type))
						category_slugs = [slug['slug'] for slug in cur.fetchall()]
						for category in category_slugs:
							if not Path(output_path, langs[lang]['path'], post_type_slugs[post_type]['slug'],
										"category",
										category).is_dir():
								continue
							pt_url = doc.createElement("url")
							pt_loc = doc.createElement("loc")
							if len(langs[lang]['path']) == 0:
								pt_loc.appendChild(
									doc.createTextNode(
										f"{self.settings['site_url']['settings_value']}/{post_type_slugs[post_type]['slug']}/category/{category}"))
							else:
								pt_loc.appendChild(
									doc.createTextNode(
										f"{self.settings['site_url']['settings_value']}/{langs[lang]['path']}/{post_type_slugs[post_type]['slug']}/category/{category}"))
							pt_url.appendChild(pt_loc)
							pt_change_freq = doc.createElement("changefreq")
							pt_change_freq.appendChild(doc.createTextNode("monthly"))
							pt_url.appendChild(pt_change_freq)
							root_node.appendChild(pt_url)
						# get tags per post type
						cur.execute("""SELECT slug FROM sloth_taxonomy 
                                                WHERE taxonomy_type = %s AND post_type = %s;""",
									('tag', post_type))
						tag_slugs = [slug['slug'] for slug in cur.fetchall()]
						for tag in tag_slugs:
							if not Path(output_path, langs[lang]['path'], post_type_slugs[post_type]['slug'], "tag",
										tag).is_dir():
								continue
							pt_url = doc.createElement("url")
							pt_loc = doc.createElement("loc")
							if len(langs[lang]['path']) == 0:
								pt_loc.appendChild(
									doc.createTextNode(
										f"{self.settings['site_url']['settings_value']}/{post_type_slugs[post_type]['slug']}/tag/{tag}"))
							else:
								pt_loc.appendChild(
									doc.createTextNode(
										f"{self.settings['site_url']['settings_value']}/{langs[lang]['path']}/{post_type_slugs[post_type]['slug']}/tag/{tag}"))
							pt_url.appendChild(pt_loc)
							pt_change_freq = doc.createElement("changefreq")
							pt_change_freq.appendChild(doc.createTextNode("monthly"))
							pt_url.appendChild(pt_change_freq)
							root_node.appendChild(pt_url)
				#   Get posts
				cur.execute("""SELECT lang, slug, post_type, update_date FROM sloth_posts;""")
				posts = cur.fetchall()
				for post in posts:
					pt_url = doc.createElement("url")
					pt_loc = doc.createElement("loc")
					if len(langs[post['lang']]['path']) == 0:
						pt_loc.appendChild(
							doc.createTextNode(
								f"{self.settings['site_url']['settings_value']}/{post_type_slugs[post['post_type']]['slug']}/{post['slug']}"))
					else:
						pt_loc.appendChild(
							doc.createTextNode(
								f"{self.settings['site_url']['settings_value']}/{langs[post['lang']]['path']}/{post_type_slugs[post['post_type']]['slug']}/{post['slug']}"))
					pt_url.appendChild(pt_loc)
					pt_change_freq = doc.createElement("changefreq")
					pt_change_freq.appendChild(doc.createTextNode("monthly"))
					pt_url.appendChild(pt_change_freq)
					pt_last_mod = doc.createElement("lastmod")
					pt_last_mod.appendChild(
						doc.createTextNode(datetime.fromtimestamp(post['update_date'] / 1000).strftime("%Y-%m-%d")))
					pt_url.appendChild(pt_last_mod)
					root_node.appendChild(pt_url)
		except Exception as e:
			print(e)
			traceback.print_exc()

		with codecs.open(os.path.join(output_path, "sitemap.xml"), "w", "utf-8") as f:
			f.write(doc.toprettyxml())
