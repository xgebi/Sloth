import unittest
import os

from app.toes.toes import Toe


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.toe = Toe(path_to_templates=os.path.join(os.getcwd(), "resources", "toes", "paragraph.md"),
                       template="empty.toe", data={"num": 3, "items": [1, 2, 3, 4]})
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
