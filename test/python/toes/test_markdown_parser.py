import unittest
import os

from app.toes.markdown_parser import MarkdownParser


class MyTestCase(unittest.TestCase):

    def test_empty_file_returns_empty(self):
        mdp = MarkdownParser(path=os.path.join(os.getcwd(), "resources", "markdown", "empty.md"))
        empty_string = mdp.to_html_string()
        self.assertEqual(empty_string, "")

    def test_two_paragraphs_file(self):
        # Assume
        mdp = MarkdownParser(path=os.path.join(os.getcwd(), "resources", "markdown", "paragraph.md"))
        two_paragraphs = mdp.to_html_string()
        # Assert
        self.assertEqual(two_paragraphs.count("<p>"), 2)
        self.assertEqual(two_paragraphs.count("</p>"), 2)

    def test_styled_paragraph(self):
        mdp = MarkdownParser(path=os.path.join(os.getcwd(), "resources", "markdown", "styled_paragraph.md"))
        result = mdp.to_html_string()
        print(result)

    def test_headlines(self):
        # Assume
        mdp = MarkdownParser(path=os.path.join(os.getcwd(), "resources", "markdown", "headlines.md"))
        headlines = mdp.to_html_string()
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
        text = mdp.to_html_string()

        print(text)
        #self.assertEqual(text.count("<img "), 1)
        #self.assertEqual(text.count("<a href"), 2)

    def test_paragraph_with_footnote(self):
        mdp = MarkdownParser(path=os.path.join(os.getcwd(), "resources", "markdown", "paragraph_with_footnotes.md"))
        text = mdp.to_html_string()

        #self.assertEqual(text.count("id='footnote-link-"), 2)
        #self.assertEqual(text.count("href='#footnote-"), 4)
        print(text)

    def test_paragraph_with_list(self):
        mdp = MarkdownParser(path=os.path.join(os.getcwd(), "resources", "markdown", "paragraph_with_list.md"))
        text = mdp.to_html_string()
        print(text)


    def test_paragraph_with_code(self):
        mdp = MarkdownParser(path=os.path.join(os.getcwd(), "resources", "markdown", "paragraph_with_code.md"))
        text = mdp.to_html_string()

        self.assertIn("<span class='code'>raichu</span>", text)
        self.assertIn("<span class='code'>pika?</span>", text)
        self.assertIn("""<pre><code class='language-javascript'>const i = 3;

<p>const j = 4;</p>
</code></pre>""", text)

    def test_custom_forms(self):
        pass

    def test_paragraph_with_code(self):
        mdp = MarkdownParser(path=os.path.join(os.getcwd(), "resources", "markdown", "real_text.md"))
        text = mdp.to_html_string()
        print(text)

    def test_basic_lists(self):
        bl = MarkdownParser(path=os.path.join(os.getcwd(), "resources", "markdown", "basic_list.md"))
        text = bl.to_html_string()

        print(text)

    def test_link_in_footnote(self):
        mdp = MarkdownParser(path=os.path.join(os.getcwd(), "resources", "markdown", "link_in_footnote.md"))
        text = mdp.to_html_string()

        self.assertEqual(text, "<p>Give a flying flamingo<sup><a href='#footnote-3' id='footnote-link-3'>3.</a></sup> is the third resource.</p><h2>Footnotes</h2><ol><li id='footnote-3'>Thanks to <a href=\"https://en.wikipedia.org/wiki/John_Bercow\">John Bercow</a> for giving us PG alternatives to swear words<a href='#footnote-link-3'>🔼3</a></li></ol>")

    # TODO figure out how to test better lists
    def test_nested_numeric_lists(self):
        bl = MarkdownParser(path=os.path.join(os.getcwd(), "resources", "markdown", "nested_numeric_list.md"))
        text = bl.to_html_string()

        print(text)

    def test_nested_numeric_lists(self):
        bl = MarkdownParser(path=os.path.join(os.getcwd(), "resources", "markdown", "nested_numeric_list_weird.md"))
        text = bl.to_html_string()

        print(text)

    def test_nested_points_lists(self):
        bl = MarkdownParser(path=os.path.join(os.getcwd(), "resources", "markdown", "nested_points_list.md"))
        text = bl.to_html_string()

        print(text)

    def test_nested_points_lists_off(self):
        bl = MarkdownParser(path=os.path.join(os.getcwd(), "resources", "markdown", "nested_points_list_weird.md"))
        text = bl.to_html_string()

        print(text)

    def test_nested_mixed_lists(self):
        bl = MarkdownParser(path=os.path.join(os.getcwd(), "resources", "markdown", "nested_mixed_list.md"))
        text = bl.to_html_string()

        print(text)


if __name__ == '__main__':
    unittest.main()
