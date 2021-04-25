import json
import os
import re
from typing import Dict, List
import html

from app.toes.node import Node
from app.toes.root_node import RootNode
from app.toes.text_node import TextNode
from app.toes.comment_node import CommentNode
from app.toes.toes_exceptions import ToeProcessingException
from app.toes.xml_parser import XMLParser
from app.toes.hooks import Hooks


def render_toe_from_path(
        *args,
        template,
        path_to_templates,
        data: Dict = {},
        hooks: Hooks = {},
        **kwargs):
    if path_to_templates is None and template is None:
        return None

    toe_engine = Toe(path_to_templates=path_to_templates, template_name=template, data=data, hooks=hooks, base_path=path_to_templates, **kwargs)
    return toe_engine.process_tree()


def render_toe_from_string(
        *args, template: str, data: Dict = {}, hooks: Hooks = {}, base_path=None, **kwargs):
    if template is None:
        return None

    toe_engine = Toe(template_string=template, data=data, hooks=hooks, base_path=base_path, **kwargs)
    return toe_engine.process_tree()


class Toe:
    tree: RootNode = None
    new_tree: RootNode = None
    path_to_templates = ""
    template_load_error = False
    variables = None
    current_scope = None

    def __init__(
            self,
            path_to_templates=None,
            template_name=None,
            data: Dict = {},
            template_string: str = None,
            hooks: Hooks = {},
            base_path = None,
            **kwargs
    ):
        self.current_new_tree_node: Node = None
        self.base_path = base_path
        if not (path_to_templates is None and template_name is None):
            self.path_to_templates = path_to_templates

            self.variables = VariableScope(data, None)
            self.current_scope = self.variables
            self.hooks = hooks
            self.new_tree = RootNode(html=True)
            self.new_tree.children = []  # This is a weird
            node = Node(
                name='html',
                parent=self.new_tree
            )
            node.children = []  # This is a weird
            self.current_new_tree_node = node
            self.new_tree.add_child(node)

            for node in self.new_tree.children:
                if node.type == Node.NODE:
                    lang = self.current_scope.find_variable('lang')
                    node.set_attribute(name='lang', value=lang if lang is not None else 'en')

            xp = XMLParser(path=(os.path.join(path_to_templates, template_name)))
            self.tree = xp.parse_file()
        elif template_string is not None:
            self.variables = VariableScope(data, None)
            self.current_scope = self.variables
            self.hooks = hooks
            self.new_tree = RootNode(html=True)
            self.new_tree.children = []  # This is a weird
            node = Node(
                name='html',
                parent=self.new_tree
            )
            node.children = []  # This is a weird
            self.current_new_tree_node = node
            self.new_tree.add_child(node)

            for node in self.new_tree.children:
                if node.type == Node.NODE:
                    lang = self.current_scope.find_variable('lang')
                    node.set_attribute(name='lang', value=lang if lang is not None else 'en')
            xp = XMLParser(template=template_string)
            self.tree = xp.parse_file()
        else:
            raise ToeProcessingException("Template not available")


    def process_tree(self):
        # There can only be one root element
        if len(self.tree.children) != 1:
            return None

        for node in self.tree.children:
            if node.get_name() == "html":
                for sub_html_node in node.children:
                    self.process_subtree(self.current_new_tree_node, sub_html_node)
            else:
                self.process_subtree(self.current_new_tree_node, node)
        del self.tree
        return self.new_tree.to_html_string()

    def process_subtree(self, new_tree_parent: Node, template_tree_node: Node):
        """
		Params:
			new_tree_parent: Document or Node object
			tree: Document or Node object
		Returns
			Document or Node object
		"""
        if template_tree_node.type == Node.TEXT:
            return new_tree_parent.add_child(TextNode(content=template_tree_node.content.strip()))

        if template_tree_node.type == Node.COMMENT:
            return new_tree_parent.add_child(CommentNode(content=template_tree_node.content.strip()))

        # check for toe attributes
        attributes = list(template_tree_node.attributes.keys())
        if 'toe:if' in attributes:
            return self.process_if_attribute(new_tree_parent, template_tree_node)
        if 'toe:for' in attributes:
            return self.process_for_attribute(new_tree_parent, template_tree_node)
        if 'toe:while' in attributes:
            return self.process_while_attribute(new_tree_parent, template_tree_node)

        # check for toe tags
        if template_tree_node.get_name().startswith('toe:'):
            return self.process_toe_tag(new_tree_parent, template_tree_node)

        # append regular element to parent element
        new_tree_node = new_tree_parent.add_child(
            Node(
                name=template_tree_node.get_name(),
                attributes={},
                children=[]
            )
        )

        for attribute in attributes:
            if attribute != "toe:class" and attribute.startswith("toe:") and attribute[len("toe:"):] in attributes:
                del template_tree_node.attributes[attribute[len("toe:"):]]

        attributes = template_tree_node.attributes.keys()
        ignore_children = False
        for attribute in attributes:
            if attribute.startswith('class'):
                if new_tree_node.has_attribute('class'):
                    new_tree_node.set_attribute(
                        f"{new_tree_node.get_attribute('class').strip()} {template_tree_node.get_attribute(attribute)}"
                    )
                else:
                    new_tree_node.set_attribute(attribute, template_tree_node.get_attribute(attribute))
            elif not attribute.startswith('toe:'):
                new_tree_node.set_attribute(attribute, template_tree_node.get_attribute(attribute))
            elif attribute.startswith('toe:text'):
                ignore_children = True
                new_tree_node.add_child(TextNode(
                    content=html.escape(str(self.process_toe_value(template_tree_node.get_attribute(attribute))))
                ))
            elif attribute.startswith('toe:content'):
                ignore_children = True
                new_tree_node.add_child(TextNode(
                    content=str(self.process_toe_value(template_tree_node.get_attribute(attribute)))
                ))
            elif attribute.startswith('toe:inline-js'):
                ignore_children = True
                self.process_inline_js(new_tree_node, template_tree_node.children)
            elif attribute.startswith('toe:class'):
                self.process_conditional_css_classes(new_tree_node, template_tree_node.get_attribute(attribute))
            else:
                new_tree_node.set_attribute(
                    attribute[attribute.find(":") + 1:],
                    self.process_toe_value(template_tree_node.get_attribute(attribute))
                )

        if template_tree_node.is_paired() and not ignore_children:
            for template_child in template_tree_node.children:
                self.process_subtree(new_tree_parent=new_tree_node, template_tree_node=template_child)

        return new_tree_node

    def process_conditional_css_classes(self, new_tree_node: Node, cond_attr: str):
        classes = ""
        if new_tree_node.has_attribute('class'):
            classes = new_tree_node.get_attribute('class').strip()
        if cond_attr[0] == "'" or cond_attr[0] == '"':
            processed_class = self.process_css_class_condition(condition=cond_attr)
            classes += processed_class if processed_class is not None else ""
        elif cond_attr[0] == "{" and cond_attr[-1] == "}":
            conditions = cond_attr[1:-1].split(",")
            for condition in conditions:
                processed_class = self.process_css_class_condition(condition=condition.strip())
                classes += f" {processed_class}" if processed_class is not None else ""
        new_tree_node.set_attribute('class', classes)

    def process_css_class_condition(self, condition: str) -> str or None:
        quote_mark = condition[0]
        sides = condition.split(":")
        if sides[0].strip()[-1] != quote_mark:
            raise ValueError('Condition value not finished')
        if self.process_condition(sides[1].strip()):
            return sides[0].strip()[1: -1]
        return None

    def process_inline_js(self, new_tree, nodes: List[TextNode]):
        for node in nodes:
            while node.content.count("<(") > 0:
                start = node.content.rfind("<(")
                end = node.content.rfind(")>")
                resolved = self.process_toe_value(node.content[start + 2: end].strip())
                node.content = f"{node.content[:start]}{resolved}{node.content[end + 2:]}"
            new_tree.add_child(
                TextNode(content=node.content)
            )

    def process_toe_tag(self, parent_element: Node, element: Node):

        if element.get_name().startswith("toe:fragment"):
            if element.has_attribute('toe:content'):
                return parent_element.add_child(TextNode(
                    content=str(self.process_toe_value(element.get_attribute("toe:content")))
                ))

            for template_node in element.children:
                self.process_subtree(new_tree_parent=parent_element, template_tree_node=template_node)

        elif element.get_name() == "toe:import":
            return self.process_toe_import_tag(parent_element, element)

        elif element.get_name() == 'toe:assign':
            return self.process_assign_tag(element)

        elif element.get_name() == 'toe:create':
            return self.process_create_tag(element)

        elif element.get_name() == 'toe:modify':
            return self.process_modify_tag(element)

        elif element.get_name() == 'toe:head':
            return self.process_head_hook(parent_node=parent_element)

        elif element.get_name() == 'toe:footer':
            return self.process_footer_hook(parent_node=parent_element)

    def process_head_hook(self, parent_node: Node):
        for child in self.hooks.head:
            if self.process_condition(child.condition):
                xp = XMLParser(template=child.content)
                children = xp.parse_file().children
                for child_node in children:
                    self.process_subtree(new_tree_parent=parent_node, template_tree_node=child_node)

    def process_footer_hook(self, parent_node: Node):
        for child in self.hooks.footer:
            if self.process_condition(child.condition):
                xp = XMLParser(template=child.content)
                children = xp.parse_file().children
                for child_node in children:
                    self.process_subtree(new_tree_parent=parent_node, template_tree_node=child_node)

    def process_toe_import_tag(self, generated_tree, element):
        file_name = element.get_attribute('file')

        if file_name.endswith(".toe.html") or file_name.endswith(".toe.xml"):
            xp = XMLParser(path=os.path.join(self.path_to_templates, file_name), base_path=self.base_path)
            imported_tree = xp.parse_file()

            for child in imported_tree.children:
                self.process_subtree(generated_tree, child)

    def process_toe_value(self, attribute_value: str) -> (str or None):
        if re.search(r"[ ]?\+[ ]?", attribute_value) is None:
            # r"[ ]?\+[ ]?" detects + so string like 'aaa' + variable can be processed
            if type(attribute_value) == str and attribute_value[0] == "'":
                return attribute_value[1: len(attribute_value) - 1]
            else:
                if attribute_value.find(" | ") >= 0:
                    return self.process_pipe(attribute_value)
                resolved_value = self.current_scope.find_variable(attribute_value)
                if resolved_value is not None:
                    return resolved_value
        else:
            var_arr = re.split(r"[ ]?\+[ ]?", attribute_value)
            if var_arr is None:
                return
            result = ""
            for item in var_arr:
                if item[0] == "'":
                    result += item[1: len(item) - 1]
                else:
                    resolved_value = self.current_scope.find_variable(item)
                    result += resolved_value if resolved_value is not None else ""

            return result

    def process_assign_tag(self, element):
        var_name = element.get_attribute('var')
        var_value = element.get_attribute('value')

        if var_name is None or len(var_name) == 0:
            raise ValueError('Variable cannot have no name')

        variable = self.current_scope.find_variable(var_name)
        if variable is None:
            raise ValueError("Variable doesn't exist")

        self.current_scope.assign_variable(var_name, var_value)
        return None

    def process_create_tag(self, element):
        var_name = element.get_attribute('var')
        var_value = element.get_attribute('value')

        if var_name is None or len(var_name) == 0:
            raise ValueError('Variable cannot have no name')

        if self.current_scope.is_variable_in_current_scope(var_name):
            raise ValueError('Variable cannot be created twice')

        self.current_scope.variables[var_name] = self.process_toe_value(var_value)
        return None

    def process_modify_tag(self, element) -> None:
        var_name = element.get_attribute('var')
        var_value = element.get_attribute('value')

        if var_name is None or len(var_name) == 0:
            raise ValueError('Variable cannot have no name')

        variable = self.current_scope.find_variable(var_name)
        if variable is None:
            raise ValueError("Variable doesn't exist")

        if element.has_attribute('toe:inc'):
            try:
                if int(variable) == float(variable):
                    self.current_scope.assign_variable(var_name, int(variable) + 1)
                else:
                    self.current_scope.assign_variable(var_name, float(variable) + 1)
            except ValueError as ve:
                raise ve

        if element.has_attribute('toe:dec'):
            try:
                if int(variable) == float(variable):
                    self.current_scope.assign_variable(var_name, int(variable) - 1)
                else:
                    self.current_scope.assign_variable(var_name, float(variable) - 1)
            except ValueError as ve:
                raise ve

        if element.has_attribute('toe:add'):
            try:
                if int(variable) == float(variable):
                    self.current_scope.assign_variable(var_name, float(variable) + float(element.get_attribute('toe:add')))
            except ValueError as ve:
                raise ve

        if element.has_attribute('toe:sub'):
            try:
                if int(variable) == float(variable):
                    self.current_scope.assign_variable(var_name, float(variable) - float(element.get_attribute('toe:sub')))
            except ValueError as ve:
                raise ve

        if element.has_attribute('toe:mul'):
            try:
                if int(variable) == float(variable):
                    self.current_scope.assign_variable(var_name, float(variable) * float(element.get_attribute('toe:mul')))
            except ValueError as ve:
                raise ve

        if element.has_attribute('toe:div'):
            try:
                if int(variable) == float(variable):
                    if float(element.get_attribute('toe:div')) != 0:
                        self.current_scope.assign_variable(var_name, float(variable) / float(element.get_attribute('toe:div')))
                        return
                    raise ZeroDivisionError()
            except ValueError as ve:
                raise ve

        if element.has_attribute('toe:mod'):
            try:
                if int(variable) == float(variable):
                    if float(element.get_attribute('toe:div')) != 0:
                        self.current_scope.assign_variable(var_name, float(variable) % float(element.get_attribute('toe:mod')))
                        return
                    raise ZeroDivisionError()
            except ValueError as ve:
                raise ve

        if element.has_attribute('toe:pow'):
            try:
                if int(variable) == float(variable):
                    self.current_scope.assign_variable(var_name, float(variable) ** float(element.get_attribute('toe:pow')))
            except ValueError as ve:
                raise ve

        return None

    def process_if_attribute(self, parent_element, element):
        if not self.process_condition(element.get_attribute('toe:if')):
            return None
        element.remove_attribute('toe:if')
        return self.process_subtree(parent_element, element)

    def process_for_attribute(self, parent_element, element):
        result_nodes = []
        # get toe:for attribute
        iterable_cond = element.get_attribute('toe:for')
        # split string between " in "
        items = iterable_cond.split(" in ")
        # find variable on the right side
        # create python for loop
        iterable_item = self.current_scope.find_variable(items[1])
        if iterable_item is None:
            return None

        element.remove_attribute('toe:for')

        for thing in iterable_item:
            # local scope creation
            local_scope = VariableScope({}, self.current_scope)
            self.current_scope = local_scope

            self.current_scope.variables[items[0]] = thing

            # process subtree
            result_node = self.process_subtree(parent_element, element)
            if result_node is not None:
                # parent_element.add_child(result_node)
                pass

            # local scope destruction
            self.current_scope = self.current_scope.parent_scope

    def process_while_attribute(self, parent_element, element):
        # get toe:for attribute
        iterable_cond = element.get_attribute('toe:while')

        contains_condition = False
        for cond in (" gt ", " gte ", " lt ", " lte ", " eq ", " neq "):
            if cond in iterable_cond:
                contains_condition = True
                break

        if not contains_condition:
            return None

        element.remove_attribute('toe:while')

        while self.process_condition(iterable_cond):
            # local scope creation
            local_scope = VariableScope({}, self.current_scope)
            self.current_scope = local_scope

            # process subtree
            result_node = self.process_subtree(parent_element, element)

            # local scope destruction
            self.current_scope = self.current_scope.parent_scope

    def process_condition(self, condition):
        if type(condition) == bool:
            return condition

        if type(condition) == str:
            condition = {
                "value": str(condition),
                "processed": False
            }

        if condition["value"][0] == "(" and condition["value"][-1] == ")":
            condition["value"] = condition["value"][1: len(condition["value"]) - 1].strip()

        condition["value"] = condition["value"].strip()
        if condition["value"].find(" ") == -1:
            if condition["value"].lower() == "true" or condition["value"].lower() == "false":
                raise ValueError('Condition not allowed')
            return self.current_scope.find_variable(condition["value"])

        if condition["value"].count(" and ") > 0 or condition["value"].count(" or ") > 0:
            return False

        if condition["value"].startswith("not "):
            return not self.process_condition(condition["value"].split(" ")[1])

        # split condition["value"] by " xxx? "
        sides = re.split(" [a-z][a-z][a-z]? ", condition["value"])
        # at least one side has to be a variable
        if len(sides) != 2:
            return False

        if sides[0].count("|") > 0 or sides[1].count("|") > 0:
            if sides[0].count("|") > 0:
                sides[0] = self.process_pipe(sides[0])
            if sides[1].count("|") > 0:
                sides[1] = self.process_pipe(sides[1])
        else:
            if not self.current_scope.is_variable(sides[0]) and not self.current_scope.is_variable(sides[1]):
                return False

        # resolve variable
        resolved = []
        for idx in range(len(sides)):
            if sides[idx][0] == "'":
                resolved.append(sides[idx][1: len(sides[idx]) - 1])
            else:
                try:
                    resolved.append(float(sides[idx]))
                except ValueError:
                    resolved_var = self.current_scope.find_variable(sides[idx])
                    if resolved_var is not None:
                        resolved.append(resolved_var)
                    else:
                        return False

        if " gte " in condition["value"]:
            return float(resolved[0]) >= float(resolved[1])
        if " gt " in condition["value"]:
            return float(resolved[0]) > float(resolved[1])
        if " lte " in condition["value"]:
            return float(resolved[0]) <= float(resolved[1])
        if " lt " in condition["value"]:
            return float(resolved[0]) < float(resolved[1])
        if " neq " in condition["value"]:
            return resolved[0] != resolved[1]
        if " eq " in condition["value"]:
            return resolved[0] == resolved[1]
        return False

    def process_pipe(self, side: str):
        actions = side.split("|")
        if not self.current_scope.is_variable(actions[0].strip()):
            return None
        value = self.current_scope.find_variable(actions[0].strip())
        for i in range(1, len(actions)):
            if actions[i].strip() == 'length':
                value = len(value)
            elif actions[i].strip() == 'json':
                value = json.dumps(value)
        return str(value)


class VariableScope:
    variables = {}
    parent_scope = None

    def __init__(self, variable_dict, parent_scope=None):
        self.variables = variable_dict if variable_dict is not None else {}
        self.parent_scope = parent_scope

    def find_variable(self, variable_name, passed_names=None):
        names = [] if passed_names is None else passed_names
        if passed_names is None and variable_name.find("['") > -1:
            names = variable_name.split("['")
            variable_name = names[0]

        if self.variables.get(variable_name) is not None:
            if len(names) > 0:
                res = self.variables.get(variable_name)
                for nidx in range(len(names) - 1):
                    if names[nidx + 1][-1] == "]":
                        names[nidx + 1] = names[nidx + 1][:-2]
                    res = res.get(names[nidx + 1])
                return res
            else:
                return self.variables[variable_name]

        if self.parent_scope is not None:
            return self.parent_scope.find_variable(variable_name, names)
        return None

    def assign_variable(self, name, value):
        if self.is_variable_in_current_scope(name):
            self.variables[name] = value
        else:
            self.parent_scope.assign_variable(name, value)

    def create_variable(self, name, value):
        if self.is_variable_in_current_scope(name):
            raise ValueError("Variable already exists")
        self.variables[name] = value

    def is_variable(self, variable_name):
        names = []
        if variable_name.find("['") > -1:
            names = variable_name.split("['")
            variable_name = names[0]

        if self.variables.get(variable_name) is not None:
            if len(names) > 0:
                res = self.variables[names[0]]
                for nidx in range(len(names) - 1):
                    if names[nidx + 1][-1] == "]":
                        names[nidx + 1] = names[nidx + 1][:-2]
                    res = res.get(names[nidx + 1])
                return res is not None
            else:
                return True

        if self.parent_scope is None:
            return False
        if self.parent_scope.is_variable(variable_name):
            return True
        return False

    def is_variable_in_current_scope(self, variable_name):
        return self.variables.get(variable_name) is not None
