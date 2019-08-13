import psycopg2
from psycopg2 import sql, errors

import threading
import time

class PostsGenerator:
	post = {}
	post_type = {}

	def __init__(self, post, post_type):
		self.post = post

	def run(self):
		t = threading.Thread(target=self.generateContent)
		t.start()

	def generateContent(self):
		for i in range(10):
			print(i)
			time.sleep(1)