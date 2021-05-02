import unittest
import os

from app.toes.toes import render_toe_from_path, render_toe_from_string


class MyTestCase(unittest.TestCase):
    """ Test Checklist
            toe:fragment ✔
            import file ✔
            toe:if ✔
            toe:for ✔
            toe:while ✔
            script toe:inline-js ✔
            toe image ✔
            toe link ✔
            toe:content ✔
            toe:text ✔
            toe hook - toe:head ✔
            toe hook - toe:footer ✔
            import file with toe code ✔
            conditions ~
            strings ~
    """
    def test_fragment_from_path(self):
        toe = render_toe_from_path(
            path_to_templates=os.path.join(os.getcwd(), "resources", "toes"),
            template="doctyped_toe_fragment_div.toe.html",
            data={}
        )
        self.assertEqual(toe, '<!DOCTYPE html><html lang="en"><div>Hello</div></html>')

    def test_fragment_from_string(self):
        with open(os.path.join(os.getcwd(), "resources", "toes", "doctyped_toe_fragment_div.toe.html"), 'r') as f:
            toe = render_toe_from_string(
                template=f.read(),
                data={}
            )
            self.assertEqual(toe, '<!DOCTYPE html><html lang="en"><div>Hello</div></html>')

    def test_importing_file(self):
        toe = render_toe_from_path(
            path_to_templates=os.path.join(os.getcwd(), "resources", "toes"),
            template="importer.toe.html",
            data={}
        )
        self.assertEqual(toe, '<!DOCTYPE html><html lang="en"><div>Hello</div></html>')

    def test_toeless_template(self):
        toe = render_toe_from_path(
            path_to_templates=os.path.join(os.getcwd(), "resources", "toes"),
            template="basic.toe.html",
            data={}
        )
        self.assertEqual(toe, '<!DOCTYPE html><html lang="en"><body><h1>Hello</h1></body></html>')

    def test_importing_file_if(self):
        toe = render_toe_from_path(
            path_to_templates=os.path.join(os.getcwd(), "resources", "toes"),
            template="importer_if.toe.html",
            data={
                "thisTrue": True
            }
        )
        self.assertEqual(toe, '<!DOCTYPE html><html lang="en"><div>Hello</div></html>')

    def test_image(self):
        toe = render_toe_from_path(
            path_to_templates=os.path.join(os.getcwd(), "resources", "toes"),
            template="toe_image.toe.html",
            data={
                "linkToImage": "/image.svg",
                "descriptionText": "Description from toes"
            }
        )
        self.assertEqual(toe, '<!DOCTYPE html><html lang="en"><img src="/image.svg" alt="Description from toes" /></html>')

    def test_importing_link(self):
        toe = render_toe_from_path(
            path_to_templates=os.path.join(os.getcwd(), "resources", "toes"),
            template="toe_link.toe.html",
            data={
                "thisTrue": True
            }
        )
        self.assertEqual(toe, '<!DOCTYPE html><html lang="en"><a href="/#">Link</a></html>')

    def test_text(self):
        toe = render_toe_from_path(
            path_to_templates=os.path.join(os.getcwd(), "resources", "toes"),
            template="toe_text.toe.html",
            data={
                "strInVar": "Hello"
            }
        )
        self.assertEqual(toe, '<!DOCTYPE html><html lang="en"><div>Hello</div><!-- note strInVar shouldn\'t have html --><div>I override but HTML formatting is applied &lt;br /&gt;</div></html>')

    def test_content(self):
        toe = render_toe_from_path(
            path_to_templates=os.path.join(os.getcwd(), "resources", "toes"),
            template="toe_content.toe.html",
            data={
                "strInVar": "Hello"
            }
        )
        self.assertEqual(toe, '<!DOCTYPE html><html lang="en"><div>Hello</div><!-- note strInVar should have html --><div>I override <br /></div></html>')

    def test_footer(self):
        # As it is now, head and footer have same implementation. When they diverge second test needs to be added
        toe = render_toe_from_path(
            path_to_templates=os.path.join(os.getcwd(), "resources", "toes"),
            template="toe_footer.toe.html",
            data={
                "strInVar": "Hello"
            },
            hooks={
                "footer": ["<div toe:text='strInVar'></div>"]
            }
        )
        self.assertEqual(toe, '<!DOCTYPE html><html lang="en"><div>Hello</div></html>')

    def test_inline_script(self):
        toe = render_toe_from_path(
            path_to_templates=os.path.join(os.getcwd(), "resources", "toes"),
            template="script_inline.toe.html",
            data={
                "strInVar": "Hello"
            }
        )
        self.assertEqual(toe, """<!DOCTYPE html><html lang="en"><script>
        const myVar = "Hello";
   </script></html>""")

    def test_for(self):
        toe = render_toe_from_path(
            path_to_templates=os.path.join(os.getcwd(), "resources", "toes"),
            template="toe_for.toe.html",
            data={
                "numbers": [1, 2, 3]
            }
        )
        self.assertEqual(toe, '<!DOCTYPE html><html lang="en"><div>1</div><div>2</div><div>3</div></html>')

    def test_while(self):
        toe = render_toe_from_path(
            path_to_templates=os.path.join(os.getcwd(), "resources", "toes"),
            template="toe_while.toe.html",
            data={}
        )
        self.assertEqual(toe, '<!DOCTYPE html><html lang="en"><div>Hello</div><div>Hello</div></html>')

    def test_if_length_function(self):
        toe = render_toe_from_path(
            path_to_templates=os.path.join(os.getcwd(), "resources", "toes"),
            template="toe_if_length.toe.html",
            data={
                "myArr": ["Hello", "Hi"]
            }
        )
        self.assertEqual(toe, '<!DOCTYPE html><html lang="en"><div>Hello</div></html>')

    def test_object_variable(self):
        toe = render_toe_from_path(
            path_to_templates=os.path.join(os.getcwd(), "resources", "toes"),
            template="variable_object.toe.html",
            data={
                "arr": {
                    "key": "This is the key"
                }
            }
        )
        self.assertEqual(toe, '<!DOCTYPE html><html lang="en"><div>This is the key</div></html>')

    def test_conditional_css_classes(self):
        toe = render_toe_from_path(
            path_to_templates=os.path.join(os.getcwd(), "resources", "toes"),
            template="toe_conditional_css_classes.toe.html",
            data={
                "myCond": True,
                "anotherCond": False
            }
        )
        self.assertEqual(toe, '<!DOCTYPE html><html lang="en"><div class="basic extended">Hello</div><div class="basic">Hello</div></html>')

    def test_conditional_css_classes(self):
        toe = render_toe_from_path(
            path_to_templates=os.path.join(os.getcwd(), "resources", "toes"),
            template="compound_conditions.toe.html",
            data={
                "cond1": True,
                "cond2": False
            }
        )
        self.assertEqual(toe, '<!DOCTYPE html><html lang="en"><div class="basic extended">Hello</div><div class="basic">Hello</div></html>')

    def test_compound_conditions(self):
        toe = render_toe_from_path(
            path_to_templates=os.path.join(os.getcwd(), "resources", "toes"),
            template="compound_conditions.toe.html",
            data={
                "cond1": True,
                "cond2": False
            }
        )
        self.assertEqual(toe, '<!DOCTYPE html><html lang="en"><div>Hello</div><div>Second hello</div></html>')


if __name__ == '__main__':
    unittest.main()
