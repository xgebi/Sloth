import unittest
import os

from app.toes.toes import render_toe_from_path


class MyTestCase(unittest.TestCase):
    """ Test Checklist
            toe:fragment
            import file
            toe:if
            toe:for
            script toe:inline-js
            toe image
            toe link
            toe:content
            toe:text
            toe hooks - toe:head, toe:footer
            import file with toe code
    """
    def test_fragment_from_path(self):
        toe = render_toe_from_path(
            path_to_templates=os.path.join(os.getcwd(), "resources", "toes"),
            template="doctyped_toe_fragment_div.toe.html",
            data={}
        )
        self.assertEqual(toe, '<!DOCTYPE html><html lang="en"><div>Hello</div></html>')

    def test_fragment_from_string(self):
        # self.toe = render_toe_from_path(
        #     path_to_templates=os.path.join(os.getcwd(), "resources", "toes"),
        #     template="doctyped_toe_fragment_div.toe.html",
        #     data={}
        # )
        # self.assertEqual(True, False)
        pass


if __name__ == '__main__':
    unittest.main()
