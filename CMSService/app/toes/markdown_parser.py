import copy
from typing import Dict, List
import re
import math
import json
from app.toes.hooks import Hooks


class ListInfo:
	indent = 2

	def __init__(self, parent=None, list_type=None):
		self.level = -1 if parent is None else parent.level + 1
		self.type = list_type
		self.parent = parent


class Footnote:
	def __init__(self, index: str or int, footnote: str):
		self.index = index
		self.footnote = footnote


def combine_footnotes(text: str, footnotes: List[Footnote]) -> str:
	if footnotes is None:
		return text
	footnotes.sort(key=lambda f: f.index)
	footnotes_str = "\n".join([footnote.footnote for footnote in footnotes])
	if len(footnotes) > 0:
		return f"{text}<h2>Footnotes</h2><ol>{footnotes_str}</ol>"
	return text


class ParsingInfo:
	def __init__(self):
		self.i = 0
		self.list_info = ListInfo()
		self.footnotes: List[Footnote] = []

	def move_index(self, step: int = 1):
		self.i += step


class MarkdownParser:
	def __init__(self, *args, path=None, **kwargs):
		if path:
			with open(path, mode="r", encoding="utf-8") as text_file:
				self.text = text_file.read()
		else:
			self.text = ""

	def to_html_string(self, text: str = "", forms: Dict = None, hooks: Hooks = None, footnote: bool = False) -> (str, List[Footnote]):
		if forms is not None:
			self.forms = forms
		if hooks is not None:
			self.hooks = hooks
		# refactoring candidate
		if text:
			self.text = text
		if len(self.text) == 0:
			return self.text, []
		if self.text is None:
			return "Error: empty text"

		result = self.text
		parsing_info = ParsingInfo()
		while parsing_info.i < len(result):
			if result[parsing_info.i] == "`":
				# parse code
				result, parsing_info = self.parse_code_block(result, parsing_info)
			elif result[parsing_info.i] == '-' or result[parsing_info.i] == '*':
				# parse horizontal line, unordered list, bold and italic
				if result[parsing_info.i: parsing_info.i + 3] == '---':
					result, parsing_info = self.parse_horizontal_line(text=result, parsing_info=parsing_info)
				else:
					# catches for italic and bold are caught inside
					result, parsing_info = self.parse_unordered_list(result, parsing_info)
			elif result[parsing_info.i].isdigit():
				# parse ordered list
				result, parsing_info = self.parse_ordered_list(result, parsing_info)
			elif result[parsing_info.i] == ">":
				if result[parsing_info.i - 2: parsing_info.i + 2] == "\n\n> " or \
						parsing_info.i == 0:
					result, parsing_info = self.parse_bloquote(result, parsing_info)
				else:
					parsing_info.move_index()
			elif result[parsing_info.i] == "[":
				# parse footnote and link
				result, parsing_info = self.parse_square_brackets(text=result, parsing_info=parsing_info)
			elif len(result) > parsing_info.i + 2 and result[parsing_info.i:parsing_info.i + 2] == "![":
				# parse image
				result, parsing_info = self.parse_image(text=result, parsing_info=parsing_info)
			elif result[parsing_info.i] == "#":
				# parse list
				if parsing_info.i == 0 or (result[parsing_info.i - 1] != "\\" and result[parsing_info.i - 1] == "\n"):
					result, parsing_info = self.parse_headline(text=result, parsing_info=parsing_info)
				else:
					parsing_info.move_index()
			elif not result[parsing_info.i].isspace() and not footnote:
				# parse paragraph
				result, parsing_info = self.parse_paragraph(text=result, parsing_info=parsing_info)
			elif result[parsing_info.i] == '\n':
				# check for endings and stuff
				if len(result) > parsing_info.i + 1 and result[parsing_info.i + 1] == '\n':
					result, parsing_info = self.end_tags(text=result, parsing_info=parsing_info)
				else:
					parsing_info.move_index()
			else:
				# deal with the rest
				parsing_info.move_index()
		# clean up after parse
		result, parsing_info = self.end_tags(text=result, parsing_info=parsing_info)
		# add footnotes
		if not footnote:
			result, parsing_info = self.add_footnotes(text=result, parsing_info=parsing_info)

		return result, parsing_info.footnotes

	def parse_square_brackets(self, text: str, parsing_info: ParsingInfo) -> (str, ParsingInfo):
		j = self.get_end_boundary_within_characters(parsing_info.i, "[", "]", text)
		footnote_pattern = re.compile(r"\[\d+\. .+?\]")
		if text[j+1] == "(":
			k = self.get_end_boundary_within_characters(j + 1, "(", ")", text)
			label = text[parsing_info.i + 1:j]
			url = text[j + 2: k]
			link_code = f"<a href=\"{url}\">{label}</a>"
			text = f"{text[:parsing_info.i]}{link_code}{text[k+1:]}"
			parsing_info.move_index(len(f"<a href=\"{url}\">"))

		elif footnote_pattern.match(text[parsing_info.i:j+1]):
			raw_footnote = text[parsing_info.i + 1: j]
			index = raw_footnote[:raw_footnote.find(". ")]
			footnote_content = raw_footnote[raw_footnote.find(". ") + 2:]
			footnote_code = f"<sup><a href='#footnote-{index}' id='footnote-link-{index}'>{index}.</a></sup>"
			text = f"{text[:parsing_info.i]}{footnote_code}{text[j + 1:]}"

			parsing_info.footnotes.append(
				Footnote(index=index, footnote=footnote_content)
			)
			parsing_info.move_index(len(footnote_code))
		else:
			parsing_info.move_index()
		return text, parsing_info

	def get_end_boundary_within_characters(self, j: int, start_char: str, end_char: str, text: str):
		end = -1
		in_code = False
		bracket_count = 0
		while j < len(text):
			if text[j] == "`":
				in_code = not in_code
				if text[j: j + 3] == "```":
					j += 3
				else:
					j += 1
			elif text[j] == start_char and not in_code:
				bracket_count += 1
				j += 1
			elif text[j] == end_char and not in_code:
				bracket_count -= 1
				if bracket_count == 0:
					end = j
					break
				j += 1
			else:
				j += 1

		return end

	def parse_bloquote(self, text: str, parsing_info: ParsingInfo) -> (str, ParsingInfo):
		# Very Work In Progress
		j = parsing_info.i + 1
		quote = ""

		end = text[j:].find("\n")
		alt_end = text[j:].find("\n>")
		if alt_end != -1 and end < alt_end:
			text = f"{text[:parsing_info.i]}<blockquote>{text[parsing_info.i + 1: end + parsing_info.i + 1].strip()}</blockquote>{text[end + parsing_info.i + 1:]}"
			parsing_info.move_index(len("<blockquote>"))

		elif end == alt_end:
			line = ""
			while j < len(text):
				end = text[j:].find("\n\n")
				alt_end = text[j:].find("\n>") + j if text[j:].find("\n>") != -1 else len(text)
				line_end = text[j:].find("\n") + j if text[j:].find("\n") != -1 else len(text)

				line += text[j + 1: alt_end if alt_end <= line_end else line_end]
				j = (alt_end if alt_end <= line_end else line_end) + 2
				if line[::-1].startswith("  "):
					line = f"{line[:-2]}<br />"

				if line_end > len(text):
					text = f"{text[:parsing_info.i]}<blockquote>{line.strip()}</blockquote>"
					parsing_info.move_index(len("<blockquote>"))
					break
				if line_end == len(text):
					line += text[j:]
					text = f"{text[:parsing_info.i]}<blockquote>{line.strip()}</blockquote>"
					parsing_info.move_index(len("<blockquote>"))
					break
				if text[line_end + 1] == "\n":
					text = f"{text[:parsing_info.i]}<blockquote>{line.strip()}</blockquote>{text[line_end + 1:]}"
					parsing_info.move_index(len("<blockquote>"))
					break

		return text, parsing_info

	def parse_horizontal_line(self, text: str, parsing_info: ParsingInfo) -> (str, ParsingInfo):
		text = f"{text[parsing_info.i - 1:]}<hr />{text[parsing_info.i + 3:]}"
		parsing_info.i += len("<hr />")
		return text, parsing_info

	def parse_headline(self, text: str, parsing_info: ParsingInfo) -> (str, ParsingInfo):
		level = len(text[parsing_info.i:text[parsing_info.i:].find(" ") + parsing_info.i])
		end_of_line = text[parsing_info.i:].find("\n")
		tail = text[end_of_line + parsing_info.i:] if end_of_line >= 0 else ""
		if text[parsing_info.i:text[parsing_info.i:].find("\n") + parsing_info.i].find("{#") > -1 \
				or (text[parsing_info.i:].find("\n") == -1 and text[parsing_info.i:].find("{#") > -1):
			id_start = text[parsing_info.i:].find("{#")
			id = text[id_start + parsing_info.i + 3: text[parsing_info.i:].find("}") + parsing_info.i - 1]
			content = text[parsing_info.i + level + 1: text[parsing_info.i:].find(" {#") + parsing_info.i]
			text = f"{text[:parsing_info.i]}<h{level} id=\"{id}\">{content}</h{level}>{tail}"
			parsing_info.i += len(f"<h{level} id=\"{id}\">")
		else:
			old_length = len(text[parsing_info.i: text[parsing_info.i:].find("\n") + parsing_info.i])
			content = text[parsing_info.i + level + 1: text[parsing_info.i:].find("\n") + parsing_info.i] if text[
																											 parsing_info.i:].find(
				"\n") >= 0 else text[parsing_info.i + level:]
			text = f"{text[:parsing_info.i]}<h{level}>{content.strip()}</h{level}>{tail}"
			parsing_info.i += len(f"<h{level}>")

		return text, parsing_info

	def parse_ordered_list(self, text: str, parsing_info: ParsingInfo) -> (str, ParsingInfo):
		line_start = text[:parsing_info.i].rfind("\n") + 1
		line_end = text[parsing_info.i:].find("\n") + parsing_info.i if text[parsing_info.i:].find(
			"\n") != -1 else len(text)
		line = text[line_start: line_end]
		numeric_list_pattern = re.compile(r"^(\d+\. )")
		if numeric_list_pattern.match(line.strip()):
			content_start = parsing_info.i + line.strip().find(' ') + 1
			if parsing_info.list_info.level == -1:
				text = f"{text[:line_start]}<ol>\n<li>{text[content_start:]}"
				parsing_info.i += len("<ol>\n<li>")
				parsing_info.list_info = ListInfo(parent=parsing_info.list_info, list_type=1)
			elif parsing_info.list_info.level == 0:
				if len(text[line_start: parsing_info.i]) > 0:
					ListInfo.indent = len(text[line_start: parsing_info.i])
					text = f"{text[:line_start]}<ol><li>{text[content_start:]}"
					new_list = ListInfo(parent=parsing_info.list_info, list_type=1)
					parsing_info.list_info = new_list
					parsing_info.i += len("<ol><li>") - ListInfo.indent
				else:
					text = f"{text[:line_start]}</li><li>{text[content_start:]}"
					parsing_info.i += len("</li><li>")
			else:
				level = math.ceil(len(text[line_start: parsing_info.i]) / ListInfo.indent)
				if level == parsing_info.list_info.level:
					text = f"{text[:line_start]}</li><li>{text[content_start:]}"
					parsing_info.i += len("</li><li>") - (level * ListInfo.indent)
				elif level < parsing_info.list_info.level:
					content_tail = text[content_start:]
					text_head = text[:line_start]

					while level < parsing_info.list_info.level:
						if type(parsing_info.list_info.type) is int:
							text_head = f"{text_head}</li></ol>"
						else:
							text_head = f"{text_head}</li></ul>"
						parsing_info.list_info = parsing_info.list_info.parent

					if type(parsing_info.list_info.type) is int:
						text = f"{text_head}</li><li>{content_tail}"
					else:
						text = f"{text_head}</li><li>{content_tail}"
					parsing_info.i += (len(text_head) - len(text[:line_start])) - (level * ListInfo.indent) + len(
						"</li><li>")
				elif level > parsing_info.list_info.level:
					text = f"{text[:line_start]}<ol><li>{text[content_start:]}"
					parsing_info.i += len("</ol><li>") - (level * ListInfo.indent) - 1
					parsing_info.list_info = ListInfo(parent=parsing_info.list_info, list_type=1)
		else:
			return self.parse_paragraph(text=text, parsing_info=parsing_info)

		return text, parsing_info

	def parse_unordered_list(self, text: str, parsing_info: ParsingInfo):
		line_start = text[:parsing_info.i].rfind("\n") + 1
		line_end = text[parsing_info.i:].find("\n") + parsing_info.i if text[parsing_info.i:].find("\n") != -1 else len(
			text)
		line = text[line_start: line_end]
		points_list_pattern = re.compile(r"^([\-|\*] )")
		if points_list_pattern.match(line.strip()):
			content_start = parsing_info.i + line.strip().find(' ') + 1
			if parsing_info.list_info.level == -1:
				text = f"{text[:line_start]}<ul>\n<li>{text[content_start:]}"
				parsing_info.i += len("<ul>\n<li>")
				parsing_info.list_info = ListInfo(parent=parsing_info.list_info, list_type='a')
			elif parsing_info.list_info.level == 0:
				if len(text[line_start: parsing_info.i]) > 0:
					ListInfo.indent = len(text[line_start: parsing_info.i])
					text = f"{text[:line_start]}<ul><li>{text[content_start:]}"
					new_list = ListInfo(parent=parsing_info.list_info, list_type='a')
					parsing_info.list_info = new_list
					parsing_info.i += len("<ul><li>") - ListInfo.indent
				else:
					text = f"{text[:line_start]}</li><li>{text[content_start:]}"
					parsing_info.i += len("</li><li>")
			else:
				level = math.ceil(len(text[line_start: parsing_info.i]) / ListInfo.indent)
				if level == parsing_info.list_info.level:
					text = f"{text[:line_start]}</li><li>{text[content_start:]}"
					parsing_info.i += len("</li><li>") - (level * ListInfo.indent)
				elif level < parsing_info.list_info.level:
					content_tail = text[content_start:]
					text_head = text[:line_start]

					while level < parsing_info.list_info.level:
						if type(parsing_info.list_info.type) is int:
							text_head = f"{text_head}</li></ol>"
						else:
							text_head = f"{text_head}</li></ul>"
						parsing_info.list_info = parsing_info.list_info.parent

					if type(parsing_info.list_info.type) is int:
						text = f"{text_head}</li><li>{content_tail}"
					else:
						text = f"{text_head}</li><li>{content_tail}"
					parsing_info.i += (len(text_head) - len(text[:line_start])) - (level * ListInfo.indent) + len(
						"</li><li>")
				elif level > parsing_info.list_info.level:
					text = f"{text[:line_start]}<ul><li>{text[content_start:]}"
					parsing_info.i += len("</ul><li>") - (level * ListInfo.indent) - 1
					parsing_info.list_info = ListInfo(parent=parsing_info.list_info, list_type='a')
		else:
			return self.parse_italic_bold(text=text, parsing_info=parsing_info)
		return text, parsing_info

	def end_tags(self, text: str, parsing_info: ParsingInfo):
		if parsing_info.list_info.level != -1:
			while parsing_info.list_info.level != -1:
				text = f"{text[:parsing_info.i]}</li>\n</ol>\n{text[parsing_info.i + 1:]}" if type(
					parsing_info.list_info.type) is int else f"{text[:parsing_info.i]}</li>\n</ul>\n{text[parsing_info.i + 1:]}"
				parsing_info.list_info = parsing_info.list_info.parent
				parsing_info.i += len("</li>\n</ol>")
		else:
			parsing_info.move_index()
		return text, parsing_info

	def parse_paragraph(self, text: str, parsing_info: ParsingInfo):
		line_start = text[:parsing_info.i].rfind("\n\n") + 2 if text[:parsing_info.i].rfind("\n\n") >= 0 else 0
		alt_line_start = text[:parsing_info.i].rfind(">\n") + 2 if text[:parsing_info.i].rfind(">\n") >= 0 else 0

		if line_start < alt_line_start:
			line_start = alt_line_start

		if text[line_start:].strip().startswith("<") and \
				not (text[line_start:].startswith("<em") or text[line_start:].startswith("<strong") or \
					 text[line_start:].startswith("<span")):
			parsing_info.move_index()
			return text, parsing_info

		j = parsing_info.i
		while j < len(text):
			line_end = text[j:].find("\n\n") + j if text[j:].find("\n\n") != -1 else len(text)
			alt_line_end = text[j:].find("\n") + j if text[j:].find("\n") != -1 else len(text)

			if line_end == alt_line_end:
				line = text[line_start: line_end]
				text = f"{text[:line_start]}<p>{line}</p>{text[line_end:]}"
				parsing_info.move_index(len("<p>"))
				break
			elif alt_line_end + 1 < len(text) and "`#-*".find(text[alt_line_end + 1]) >= 0:
				line = text[line_start: alt_line_end]
				text = f"{text[:line_start]}<p>{line}</p>{text[alt_line_end:]}"
				parsing_info.move_index(len("<p>"))
				break
			elif alt_line_end + 1 < len(text) and text[alt_line_end + 1].isdigit():
				j = alt_line_end + 2
				while j < len(text) and text[j].isdigit():
					j += 1
				if text[j] == ".":
					line = text[line_start: alt_line_end]
					text = f"{text[:line_start]}<p>{line}</p>{text[alt_line_end:]}"
					parsing_info.move_index(len("<p>"))
					break
				if j == len(text):
					text = f"{text[:line_start]}<p>{text[line_start]}:</p>"
					parsing_info.move_index(len("<p>"))
					break
			elif line_end == len(text):
				line = text[line_start: line_end]
				text = f"{text[:line_start]}<p>{line.strip()}</p>"
				parsing_info.move_index(len("<p>"))
				break
			else:
				j += (alt_line_end - j) + 1

		return text, parsing_info

	def parse_code_block(self, text: str, parsing_info: ParsingInfo) -> (str, ParsingInfo):
		if (parsing_info.i - 1 < 0 or text[parsing_info.i - 1] == " " or text[parsing_info.i - 1] == ">"
			or text[parsing_info.i - 1] == "\n") and text[parsing_info.i + 1] != "`":
			j = text[parsing_info.i + 1:].find("`") + (parsing_info.i + 1)
			if (j + 1 < len(text) and text[j + 1] != "`") or (j + 1 == len(text)):
				replacement = f"<span class='code'>{text[parsing_info.i + 1:j]}</span>"
				if parsing_info.i == 0:
					text = replacement + text[j + 1:]
				else:
					text = text[:parsing_info.i] + replacement + text[j + 1:]
				parsing_info.move_index(len(replacement) - 2)
			else:
				parsing_info.move_index()
		elif (parsing_info.i - 1 < 0 or text[parsing_info.i - 1] == "\n") and text[parsing_info.i + 1] == "`" and text[
			parsing_info.i + 2] == "`":
			j = text[parsing_info.i + 3:].find("```") + (parsing_info.i + 3)
			first_line_end = text[parsing_info.i + 3:].find("\n") + (parsing_info.i + 3)
			lang = text[parsing_info.i + 3: first_line_end]
			if j != -1:
				replacement = f"<pre><code class='language-{lang.lower()}'>{text[first_line_end + 1:j]}</code></pre>"
				if parsing_info.i == 0:
					text = replacement + text[j + 3:]
				else:
					text = text[:parsing_info.i - 1] + replacement + text[j + 3:]
				parsing_info.i += len(replacement)
		else:
			parsing_info.move_index()

		return text, parsing_info

	def parse_footnote(self, text: str, parsing_info: ParsingInfo, pattern) -> (str, ParsingInfo):
		j = parsing_info.i
		end = -1
		in_code = False
		bracket_count = 0
		while j < len(text):
			if text[j] == "`":
				in_code = not in_code
				if text[j: j+3] == "```":
					j += 3
				else:
					j += 1
			elif text[j] == "[" and not in_code:
				bracket_count += 1
				j += 1
			elif text[j] == "]" and not in_code:
				bracket_count -= 1
				if bracket_count == 0:
					end = j
					break
				j += 1
			else:
				j += 1


		raw_footnote = text[parsing_info.i + 1: end]
		index = raw_footnote[:raw_footnote.find(". ")]
		footnote_content = raw_footnote[raw_footnote.find(". ") + 2:]
		footnote_code = f"<sup><a href='#footnote-{index}' id='footnote-link-{index}'>{index}.</a></sup>"
		text = f"{text[:parsing_info.i]}{footnote_code}{text[end + 1:]}"

		parsing_info.footnotes.append(
			Footnote(index=index, footnote=footnote_content)
		)
		parsing_info.move_index(len(footnote_code))
		return text, parsing_info

	def add_footnotes(self, text: str, parsing_info: ParsingInfo) -> (str, ParsingInfo):
		if len(parsing_info.footnotes) > 0:
			# TODO Make footnotes word and list type configurable
			footnotes = []
			raw_footnotes = copy.deepcopy(parsing_info.footnotes)
			i = 0
			while i < len(raw_footnotes):
				footnote_parser = MarkdownParser()
				parsed_footnote, nested_footnotes = footnote_parser.to_html_string(raw_footnotes[i].footnote, footnote=True)
				raw_footnotes.extend(nested_footnotes)
				footnotes.append(
					Footnote(
						index=raw_footnotes[i].index,
						footnote=f"<li id='footnote-{raw_footnotes[i].index}'>{parsed_footnote}<a href='#footnote-link-{raw_footnotes[i].index}'>🔼{raw_footnotes[i].index}</a></li>")
				)
				i += 1
			parsing_info.footnotes = footnotes
		return text, parsing_info

	def parse_link(self, text: str, parsing_info: ParsingInfo, pattern) -> (str, ParsingInfo):
		possible_end = pattern.match(text[parsing_info.i:]).span()[1] + parsing_info.i
		raw_link = text[parsing_info.i + 1: possible_end - 1].split("](")
		if raw_link[1].find(') ') >= 0:
			link_code = f"<a href=\"{raw_link[1][:raw_link[1].find(') ')]}\">{raw_link[0]}</a>"
			text = f"{text[:parsing_info.i]}{link_code}{text[parsing_info.i + len(raw_link[0]) + 4 + raw_link[1].find(') '):]}"
			parsing_info.move_index(len(f"<a href=\"{raw_link[1][:raw_link[1].find(') ')]}\">"))
		else:
			link_code = f"<a href=\"{raw_link[1]}\">{raw_link[0]}</a>"
			text = f"{text[:parsing_info.i]}{link_code}{text[parsing_info.i + len(raw_link[0]) + len(raw_link[1]) + 4:]}"
			parsing_info.move_index(len(f"<a href=\"{raw_link[1]}\">"))

		return text, parsing_info

	def parse_image(self, text: str, parsing_info: ParsingInfo) -> (str, ParsingInfo):
		img_pattern = re.compile(r"!\[(.*)]\((.*)\)")
		if img_pattern.match(text[parsing_info.i:]):
			img_info = text[
					   parsing_info.i:
					   img_pattern.match(text[parsing_info.i:]).span()[1] + parsing_info.i
					   ].split("](")
			img_code = f"<img alt=\"{img_info[0][2:]}\" src=\"{img_info[1][:len(img_info[1]) - 1]}\" />"
			text = f"{text[:parsing_info.i]}{img_code}{text[img_pattern.match(text[parsing_info.i:]).span()[1] + parsing_info.i:]}"
			parsing_info.move_index(len(img_code))
		else:
			parsing_info.move_index()
		return text, parsing_info

	def parse_italic_bold(self, text: str, parsing_info: ParsingInfo) -> (str, ParsingInfo):
		if text[parsing_info.i + 1:].find('*') == -1:
			is_stand_alone = True
		elif text[parsing_info.i + 1:].find('\n') == -1 and text[parsing_info.i + 1:].find('*') >= 0:
			is_stand_alone = False
		else:
			is_stand_alone = text[parsing_info.i + 1:].find('*') > text[parsing_info.i + 1:].find('\n')
		if is_stand_alone:
			parsing_info.move_index()
		else:
			if text[parsing_info.i: parsing_info.i + 3] == "***":
				end_italics = text[parsing_info.i + 1:].find('***') + parsing_info.i + 1
				text = f"{text[:parsing_info.i]}<strong><em>{text[parsing_info.i + 3: end_italics]}</em></strong>{text[end_italics + 3:]}"
				parsing_info.move_index(len("<strong><em>"))
			elif text[parsing_info.i: parsing_info.i + 2] == "**":
				end_bold = text[parsing_info.i + 1:].find('**') + parsing_info.i + 1
				text = f"{text[:parsing_info.i]}<strong>{text[parsing_info.i + 2: end_bold]}</strong>{text[end_bold + 2:]}"
				parsing_info.move_index(len("<strong>"))
			else:
				end_italics = text[parsing_info.i + 1:].find('*') + parsing_info.i + 1
				text = f"{text[:parsing_info.i]}<em>{text[parsing_info.i + 1: end_italics]}</em>{text[end_italics + 1:]}"
				parsing_info.move_index(len("<em>"))

		return text, parsing_info
