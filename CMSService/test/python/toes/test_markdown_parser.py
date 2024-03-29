import unittest
import os

from app.toes.markdown_parser import MarkdownParser, combine_footnotes


class MyTestCase(unittest.TestCase):

	def test_empty_file_returns_empty(self):
		mdp = MarkdownParser(path=os.path.join(os.getcwd(), "resources", "markdown", "empty.md"))
		empty_string = mdp.to_html_string()[0]
		self.assertEqual(empty_string, "")

	def test_two_paragraphs_file(self):
		# Assume
		mdp = MarkdownParser(path=os.path.join(os.getcwd(), "resources", "markdown", "paragraph.md"))
		two_paragraphs = mdp.to_html_string()[0]
		# Assert
		self.assertEqual(two_paragraphs.count("<p>"), 2)
		self.assertEqual(two_paragraphs.count("</p>"), 2)

	def test_styled_paragraph(self):
		mdp = MarkdownParser(path=os.path.join(os.getcwd(), "resources", "markdown", "styled_paragraph.md"))
		result = mdp.to_html_string()[0]
		print(result)

	def test_headlines(self):
		# Assume
		mdp = MarkdownParser(path=os.path.join(os.getcwd(), "resources", "markdown", "headlines.md"))
		headlines = mdp.to_html_string()[0]
		# Assert
		self.assertEqual(headlines.count("<h1"), 1)
		self.assertEqual(headlines.count("</h1>"), 1)
		self.assertEqual(headlines.count("<h2>"), 1)
		self.assertEqual(headlines.count("</h2>"), 1)
		self.assertEqual(headlines.count("<h3>"), 1)
		self.assertEqual(headlines.count("</h3>"), 1)
		self.assertEqual(headlines.count("<h4>"), 1)
		self.assertEqual(headlines.count("</h4>"), 1)
		self.assertEqual(headlines.count("<h5>"), 1)
		self.assertEqual(headlines.count("</h5>"), 1)
		self.assertEqual(headlines.count("<h6"), 1)
		self.assertEqual(headlines.count("</h6>"), 1)
		print(headlines)

	def test_paragraph_with_image_link_headlines(self):
		mdp = MarkdownParser(path=os.path.join(os.getcwd(), "resources", "markdown", "paragraph_with_image_link_headlines.md"))
		text = mdp.to_html_string()[0]

		print(text)
		#self.assertEqual(text.count("<img "), 1)
		#self.assertEqual(text.count("<a href"), 2)

	def test_paragraph_with_footnote(self):
		mdp = MarkdownParser(path=os.path.join(os.getcwd(), "resources", "markdown", "paragraph_with_footnotes.md"))
		text, footnotes = mdp.to_html_string()[0]

		#self.assertEqual(text.count("id='footnote-link-"), 2)
		#self.assertEqual(text.count("href='#footnote-"), 4)
		print(combine_footnotes(text=text, footnotes=footnotes))

	def test_paragraph_with_nested_footnote(self):
		mdp = MarkdownParser(path=os.path.join(os.getcwd(), "resources", "markdown", "paragraph_with_footnotes_with_nested_footnotes.md"))
		text, footnotes = mdp.to_html_string()[0]

		#self.assertEqual(text.count("id='footnote-link-"), 2)
		#self.assertEqual(text.count("href='#footnote-"), 4)
		print(combine_footnotes(text=text, footnotes=footnotes))

	def test_paragraph_with_list(self):
		mdp = MarkdownParser(path=os.path.join(os.getcwd(), "resources", "markdown", "paragraph_with_list.md"))
		text = mdp.to_html_string()[0]
		print(text)

	def test_block_quotes(self):
		mdp = MarkdownParser(path=os.path.join(os.getcwd(), "resources", "markdown", "block_quotes.md"))
		text = mdp.to_html_string()[0]
		print(text)

	def test_block_quotes_with_paragraphs(self):
		mdp = MarkdownParser(path=os.path.join(os.getcwd(), "resources", "markdown", "blockquotes_paragrahps.md"))
		text = mdp.to_html_string()[0]
		print(text)


	def test_paragraph_with_code(self):
		mdp = MarkdownParser(path=os.path.join(os.getcwd(), "resources", "markdown", "paragraph_with_code.md"))
		text = mdp.to_html_string()[0]

		self.assertIn("<span class='code'>raichu</span>", text)
		self.assertIn("<span class='code'>pika?</span>", text)
		self.assertIn("""<pre><code class='language-javascript'>const i = 3;

<p>const j = 4;</p>
</code></pre>""", text)

	def test_paragraph_with_code(self):
		mdp = MarkdownParser(path=os.path.join(os.getcwd(), "resources", "markdown", "real_text.md"))
		text = mdp.to_html_string()[0]
		print(text)

	def test_basic_lists(self):
		bl = MarkdownParser(path=os.path.join(os.getcwd(), "resources", "markdown", "basic_list.md"))
		text = bl.to_html_string()[0]

		print(text)

	def test_link_in_footnote(self):
		mdp = MarkdownParser(path=os.path.join(os.getcwd(), "resources", "markdown", "link_in_footnote.md"))
		text, footnotes = mdp.to_html_string()

		self.assertEqual(text, "<p>Give a flying flamingo<sup><a href='#footnote-3' id='footnote-link-3'>3.</a></sup> is the third resource.</p>")
		self.assertEqual(footnotes[0].footnote, "<li id='footnote-3'>Thanks to <a href=\"https://en.wikipedia.org/wiki/John_Bercow\">John Bercow</a> for giving us PG alternatives to swear words<a href='#footnote-link-3'>🔼3</a></li>")
		self.assertEqual(footnotes[0].index, '3')

	def test_nested_numeric_lists(self):
		bl = MarkdownParser(path=os.path.join(os.getcwd(), "resources", "markdown", "nested_numeric_list.md"))
		text = bl.to_html_string()[0]

		print(text)

	def test_nested_numeric_lists(self):
		bl = MarkdownParser(path=os.path.join(os.getcwd(), "resources", "markdown", "nested_numeric_list_weird.md"))
		text = bl.to_html_string()[0]

		print(text)

	def test_nested_points_lists(self):
		bl = MarkdownParser(path=os.path.join(os.getcwd(), "resources", "markdown", "nested_points_list.md"))
		text = bl.to_html_string()[0]

		print(text)

	def test_nested_points_lists_off(self):
		bl = MarkdownParser(path=os.path.join(os.getcwd(), "resources", "markdown", "nested_points_list_weird.md"))
		text = bl.to_html_string()[0]

		print(text)

	def test_nested_mixed_lists(self):
		bl = MarkdownParser(path=os.path.join(os.getcwd(), "resources", "markdown", "nested_mixed_list.md"))
		text = bl.to_html_string()[0]

		self.assertEqual(text, """<ul>
<li>aaa
</li><li>bbb
<ol><li>ccc
</li><li>ddd
<ul><li>eee
</li></ul></li></ol></li><li>fff</li>
</ul>

<ol>
<li>ggg
</li><li>hhh
<ul><li>iii
</li><li>JJJ
<ul><li>kkk
</li></ul></li></ul></li><li>lll</li>
</ol>
""")

	def test_list_with_inline_code(self):
		bl = MarkdownParser(path=os.path.join(os.getcwd(), "resources", "markdown", "list_with_inline_code.md"))
		text = bl.to_html_string()[0]

		self.assertEqual(text, """<ul>
<li><span class='code'>aaa</span>
</li><li><span class='code'>bbb</span>
<ol><li><span class='code'>ccc</span>
</li><li><span class='code'>ddd</span>
<ul><li><span class='code'>eee</span>
</li></ul></li></ol></li><li><span class='code'>fff</span></li>
</ul>
""")

	def test_html_link(self):
		bl = MarkdownParser(path=os.path.join(os.getcwd(), "resources", "markdown", "html.md"))
		text = bl.to_html_string()[0]

		self.assertEqual(text, '<div id="aaa"><a href="#aaa">aaa</a></div>')

	def test_html_link_with_parenthesis(self):
		bl = MarkdownParser(path=os.path.join(os.getcwd(), "resources", "markdown", "link_with_parenthesis.md"))
		text = bl.to_html_string()[0]

		self.assertEqual(text, '<p>A significant number of sports competitions have rules about foreigners. In Japan every sumo <a href="https://en.wikipedia.org/wiki/Heya_(sumo)">stable</a> (部屋, heya) has a limit of one foreigner, so at any time there are about 43. In this post I\'ll look into webscraping, filling missing data and analyzing how good they are (hint: last to top ranked wrestlers are from Mongolia).</p>')

	def test_links(self):
		bl = MarkdownParser(path=os.path.join(os.getcwd(), "resources", "markdown", "links.md"))
		text = bl.to_html_string()[0]

		self.assertEqual(text, '<p>At the moment I am learning through courses. First one is Scott Jehl\'s <a href="https://scottjehl.com/lfwp/">course on performance</a>. Second course is <a href="https://www.udemy.com/course/user-experience-design-fundamentals/">User Experience Design Fundamentals</a> because the back-end of my CMS needs improvements. Third is a <a href="https://www.udemy.com/course/hands-on-data-structures-and-algorithms-in-rust/">hands-on Rust course</a>. </p>')


if __name__ == '__main__':
	unittest.main()
