import unittest
import os

from app.toes.MarkdownParser import MarkdownParser


class MyTestCase(unittest.TestCase):

    def test_empty_file_returns_empty(self):
        mdp = MarkdownParser(path=os.path.join(os.getcwd(), "resources", "empty.md"))
        empty_string = mdp.to_html_string()
        self.assertEqual(empty_string, "")

    def test_two_paragraphs_file(self):
        # Assume
        mdp = MarkdownParser(path=os.path.join(os.getcwd(), "resources", "paragraph.md"))
        two_paragraphs = mdp.to_html_string()
        # Assert
        self.assertEqual(two_paragraphs.count("<p>"), 2)
        self.assertEqual(two_paragraphs.count("</p>"), 2)

    def test_headlines(self):
        # Assume
        mdp = MarkdownParser(path=os.path.join(os.getcwd(), "resources", "headlines.md"))
        headlines = mdp.to_html_string()
        # Assert
        self.assertEqual(headlines.count("<h1>"), 1)
        self.assertEqual(headlines.count("</h1>"), 1)
        self.assertEqual(headlines.count("<h2>"), 1)
        self.assertEqual(headlines.count("</h2>"), 1)
        self.assertEqual(headlines.count("<h3>"), 1)
        self.assertEqual(headlines.count("</h3>"), 1)
        self.assertEqual(headlines.count("<h4>"), 1)
        self.assertEqual(headlines.count("</h4>"), 1)
        self.assertEqual(headlines.count("<h5>"), 1)
        self.assertEqual(headlines.count("</h5>"), 1)
        self.assertEqual(headlines.count("<h6>"), 1)
        self.assertEqual(headlines.count("</h6>"), 1)


if __name__ == '__main__':
    unittest.main()
