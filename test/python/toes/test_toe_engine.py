import unittest
import os

from app.toes.toes import render_toe_from_path


class MyTestCase(unittest.TestCase):
    """ Test Checklist
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
    def test_something(self):
        self.toe = render_toe_from_path(
            path_to_templates=os.path.join(os.getcwd(), "resources", "toes"),
            template="toe_fragment_xml_declared.toe.html",
            data={"num": 3, "items": [1, 2, 3, 4]}
        )
        self.assertEqual(True, False)



if __name__ == '__main__':
    unittest.main()
