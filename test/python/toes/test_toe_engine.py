import unittest
import os

from app.toes.toes import render_toe


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.toe = render_toe(
            path_to_templates=os.path.join(os.getcwd(), "resources", "toes"),
            template="toe_fragment_xml_declared.toe.html",
            data={"num": 3, "items": [1, 2, 3, 4]}
        )
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
