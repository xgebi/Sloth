import unittest

from app.toes.node import Node


class MyTestCase(unittest.TestCase):
    def test_node_gets_created(self):
        node = Node(name="my-node")

        self.assertEqual(node.name, "my-node")

    def test_node_gets_created_with_attributes(self):
        node = Node(name="my-node", attributes={"attr": "1"})

        self.assertEqual(node.name, "my-node")
        self.assertEqual(node.attributes["attr"], "1")

    def test_set_new_attribute_empty_existing_attribute_1(self):
        node = Node(name="my-node", attributes={"thing", "is"})
        node.set_attribute("selected")
        self.assertIn("selected", node.attributes.keys())

    def test_set_new_attribute_empty_existing_attribute_2(self):
        node = Node(name="my-node", attributes={"thing": "is"})
        node.set_attribute("selected")
        self.assertIn("selected", node.attributes.keys())

    def test_set_new_attribute_empty(self):
        node = Node(name="my-node")
        node.set_attribute("selected")
        self.assertIn("selected", node.attributes.keys())

    def test_set_new_attribute_with_value(self):
        node = Node(name="my-node")
        node.set_attribute("selected", "true")
        self.assertEqual(node.attributes["selected"], "true")

    def test_set_existing_attribute(self):
        node = Node(name="my-node", attributes={"attr": "1"})
        self.assertEqual(node.attributes["attr"], "1")

        node.set_attribute("attr", "2")
        self.assertEqual(node.attributes["attr"], "2")

    def test_remove_attribute(self):
        node = Node(name="my-node", attributes={"selected": ""})
        node.remove_attribute("selected")
        self.assertNotIn("selected", node.attributes.keys())

    def test_add_child(self):
        parent_node = Node(name="parent-node")
        child_node = Node(name="child-node")
        parent_node.add_child(child_node)
        self.assertIn(child_node, parent_node.children)

    def test_remove_child(self):
        parent_node = Node(name="parent-node")
        child_node = Node(name="child-node")
        parent_node.add_child(child_node)
        self.assertIn(child_node, parent_node.children)
        parent_node.remove_child(child_node)
        self.assertNotIn(child_node, parent_node.children)


if __name__ == '__main__':
    unittest.main()
