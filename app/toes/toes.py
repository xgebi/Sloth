import enum
import html
import json
import os
import re
from typing import Dict, List
import copy

from app.toes.comment_node import CommentNode
from app.toes.hooks import Hooks
from app.toes.node import Node
from app.toes.root_node import RootNode
from app.toes.text_node import TextNode
from app.toes.toes_exceptions import ToeProcessingException, ToeInvalidConditionException, ToeVariableNotFoundException
from app.toes.xml_parser import XMLParser


def render_toe_from_path(
        *args,
        template,
        path_to_templates,
        data: Dict = {},
        hooks: Hooks = {},
        **kwargs):
    if path_to_templates is None and template is None:
        return None

    toe_engine = Toe(*args, path_to_templates=path_to_templates, template_name=template, data=data, hooks=hooks,
                     base_path=path_to_templates, **kwargs)
    return toe_engine.process_tree()


def render_toe_from_string(
        *args,
        template: str,
        data: Dict = {},
        hooks: Hooks = {},
        base_path=None,
        **kwargs
):
    if template is None:
        return None

    toe_engine = Toe(*args, template_string=template, data=data, hooks=hooks, base_path=base_path, **kwargs)
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
            *args,
            path_to_templates=None,
            template_name=None,
            data: Dict = {},
            template_string: str = None,
            hooks: Hooks = {},
            base_path=None,
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
                for child in template_tree_node.children:
                    if type(child) is TextNode:
                        ignore_children = True
                value = self.process_toe_value(template_tree_node.get_attribute(attribute))
                new_tree_node.add_child(TextNode(
                    content=html.escape(str(value if value is not None else ""))))
            elif attribute.startswith('toe:content'):
                ignore_children = True
                value = self.process_toe_value(template_tree_node.get_attribute(attribute))
                new_tree_node.add_child(TextNode(
                    content=str(value if value is not None else "")
                ))
            elif attribute.startswith('toe:inline-js'):
                ignore_children = True
                self.process_inline_js(new_tree_node, template_tree_node.children)
            elif attribute.startswith('toe:class'):
                self.process_conditional_css_classes(
                    new_tree_node=new_tree_node,
                    cond_attr=template_tree_node.get_attribute(attribute)
                )
            elif attribute.startswith("toe:checked") or attribute.startswith("toe:selected"):
                self.process_conditional_attributes(
                    new_tree_node=new_tree_node,
                    cond_attr=template_tree_node.get_attribute(attribute),
                    attr_name=attribute[attribute.find(":") + 1:]
                )
            elif attribute.startswith('toe:attr-'):
                new_tree_node.set_attribute(
                    attribute[len('toe:attr-'):],
                    self.process_toe_value(template_tree_node.get_attribute(attribute))
                )
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
        else:
            classes += self.current_scope.find_variable(cond_attr)
        if len(classes) > 0:
            new_tree_node.set_attribute('class', classes)

    def process_conditional_attributes(self, new_tree_node: Node, cond_attr: str, attr_name: str):
        if self.process_condition(condition=cond_attr):
            new_tree_node.set_attribute(attr_name, "")

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
                try:
                    resolved_value = float(attribute_value)
                    if resolved_value == int(attribute_value):
                        resolved_value = int(attribute_value)
                except:
                    if attribute_value.find(" | ") >= 0:
                        return self.process_pipe(attribute_value)
                    resolved_value = self.current_scope.find_variable(attribute_value)

                return resolved_value if resolved_value is not None else ""
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
                    result += str(resolved_value) if resolved_value is not None else ""

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
                    self.current_scope.assign_variable(var_name,
                                                       float(variable) + float(element.get_attribute('toe:add')))
            except ValueError as ve:
                raise ve

        if element.has_attribute('toe:sub'):
            try:
                if int(variable) == float(variable):
                    self.current_scope.assign_variable(var_name,
                                                       float(variable) - float(element.get_attribute('toe:sub')))
            except ValueError as ve:
                raise ve

        if element.has_attribute('toe:mul'):
            try:
                if int(variable) == float(variable):
                    self.current_scope.assign_variable(var_name,
                                                       float(variable) * float(element.get_attribute('toe:mul')))
            except ValueError as ve:
                raise ve

        if element.has_attribute('toe:div'):
            try:
                if int(variable) == float(variable):
                    if float(element.get_attribute('toe:div')) != 0:
                        self.current_scope.assign_variable(var_name,
                                                           float(variable) / float(element.get_attribute('toe:div')))
                        return
                    raise ZeroDivisionError()
            except ValueError as ve:
                raise ve

        if element.has_attribute('toe:mod'):
            try:
                if int(variable) == float(variable):
                    if float(element.get_attribute('toe:div')) != 0:
                        self.current_scope.assign_variable(var_name,
                                                           float(variable) % float(element.get_attribute('toe:mod')))
                        return
                    raise ZeroDivisionError()
            except ValueError as ve:
                raise ve

        if element.has_attribute('toe:pow'):
            try:
                if int(variable) == float(variable):
                    self.current_scope.assign_variable(var_name,
                                                       float(variable) ** float(element.get_attribute('toe:pow')))
            except ValueError as ve:
                raise ve

        return None

    def process_if_attribute(self, parent_element, element):
        if not self.process_condition(element.get_attribute('toe:if')):
            return None
        new_element = copy.deepcopy(element)
        new_element.remove_attribute('toe:if')
        return self.process_subtree(parent_element, new_element)

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

        for thing in iterable_item:
            new_element = copy.deepcopy(element)
            new_element.remove_attribute('toe:for')
            # local scope creation
            local_scope = VariableScope({}, self.current_scope)
            self.current_scope = local_scope

            if type(iterable_item) == dict:
                self.current_scope.variables[items[0]] = iterable_item[thing]
            else:
                self.current_scope.variables[items[0]] = thing

            # process subtree
            result_node = self.process_subtree(parent_element, new_element)
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

        new_element = copy.deepcopy(element)
        new_element.remove_attribute('toe:while')

        while self.process_condition(iterable_cond):
            # local scope creation
            local_scope = VariableScope({}, self.current_scope)
            self.current_scope = local_scope

            # process subtree
            result_node = self.process_subtree(parent_element, new_element)

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
                return condition["value"].lower() == "true"
            return self.current_scope.find_variable(condition["value"])

        if condition["value"].count(" and ") > 0 or condition["value"].count(" or ") > 0:
            return self.process_compound_condition(condition["value"])

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
            try:
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
            except Exception as e:
                print(e)

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

    def process_compound_condition(self, condition) -> bool:
        parsing_info = CompoundConditionParsingInfo(toe=self)
        while parsing_info.i < len(condition):
            # first two conditions deal with parenthesis
            if condition[parsing_info.i] == "(" and not parsing_info.in_string:
                parsing_info.current_depth += 1
                parsing_info.i += 1
            elif condition[parsing_info.i] == ")" and not parsing_info.in_string:
                parsing_info.current_depth -= 1
                parsing_info.i += 1
            # This condition deals with strings, so and, or, ( and ) are ignored in strings
            elif condition[parsing_info.i] == "\"" or condition[parsing_info.i] == "'":
                if condition[parsing_info.i - 1] != "\\":
                    parsing_info.in_string = not parsing_info.in_string
                if parsing_info.in_string and parsing_info.string_quote == condition[parsing_info.i] and condition[parsing_info.i - 1] != "\\":
                    parsing_info.string_quote = condition[parsing_info.i]
                parsing_info.i += 1
            # Next two conditions are dealing with and and or but only on 0 depth
            elif condition[parsing_info.i] == "a" and parsing_info.current_depth == 0:
                if condition[parsing_info.i - 1: parsing_info.i + len("and ")] == " and ":
                    if parsing_info.current_tree.junction == CONDITION_JUNCTION.junction_and:
                        # add part to tree
                        parsing_info.current_tree.parts.append(
                            condition[parsing_info.condition_start:parsing_info.i]
                                .strip()
                        )
                        # move index
                        parsing_info.i += len(f"and ")
                        parsing_info.condition_start = parsing_info.i
                    elif parsing_info.current_tree.junction == CONDITION_JUNCTION.junction_none:
                        # set junction
                        parsing_info.current_tree.junction = CONDITION_JUNCTION.junction_and
                        # add part to tree
                        parsing_info.current_tree.parts.append(
                            condition[parsing_info.condition_start:parsing_info.i].strip()
                        )
                        # move index
                        parsing_info.i += len(f"and ")
                        parsing_info.condition_start = parsing_info.i
                    else:
                        # create new tree
                        new_tree = ConditionTree(toe=self)
                        # set junction
                        new_tree.junction = CONDITION_JUNCTION.junction_and
                        parsing_info.current_tree.parts.append(new_tree)
                        parsing_info.current_tree = new_tree
                        # add part to tree
                        parsing_info.current_tree.parts.append(
                            condition[parsing_info.condition_start:parsing_info.i].strip()
                        )
                        # move index
                        parsing_info.i += len(f"and ")
                        parsing_info.condition_start = parsing_info.i
                else:
                    parsing_info.i += 1
            elif condition[parsing_info.i] == "o" and parsing_info.current_depth == 0:
                if condition[parsing_info.i - 1: parsing_info.i + len("or ")] == " or ":
                    if parsing_info.current_tree.junction == CONDITION_JUNCTION.junction_or:
                        # add part to tree
                        parsing_info.current_tree.parts.append(
                            condition[parsing_info.condition_start:parsing_info.i].strip()
                        )
                        # move index
                        parsing_info.i += len(f"or ")
                        parsing_info.condition_start = parsing_info.i
                    elif parsing_info.current_tree.junction == CONDITION_JUNCTION.junction_none:
                        # set junction
                        parsing_info.current_tree.junction = CONDITION_JUNCTION.junction_or
                        # add part to tree
                        parsing_info.current_tree.parts.append(
                            condition[parsing_info.condition_start:parsing_info.i]
                                .strip()
                        )
                        # move index
                        parsing_info.i += len(f"or ")
                        parsing_info.condition_start = parsing_info.i
                    else:
                        # create new tree
                        new_tree = ConditionTree(toe=self)
                        # set junction
                        new_tree.junction = CONDITION_JUNCTION.junction_or
                        parsing_info.current_tree.parts.append(new_tree)
                        parsing_info.current_tree = new_tree
                        # add part to tree
                        parsing_info.current_tree.parts.append(
                            condition[parsing_info.condition_start:parsing_info.i].strip()
                        )
                        # move index
                        parsing_info.i += len(f"or ")
                        parsing_info.condition_start = parsing_info.i
                else:
                    parsing_info.i += 1
            else:
                parsing_info.i += 1
        parsing_info.current_tree.parts.append(
            condition[parsing_info.condition_start:].strip()
        )

        return parsing_info.top_tree.process_tree()

    def process_pipe(self, side: str):
        actions = side.split("|")
        if self.current_scope.is_variable(actions[0].strip()) is None:
            return None
        value = self.current_scope.find_variable(actions[0].strip())
        for i in range(1, len(actions)):
            if value is None:
                return ""
            if actions[i].strip() == 'length':
                value = len(value)
            elif actions[i].strip() == 'json':
                value = json.dumps(value)
        return str(value)


class ConditionTree:
    def __init__(self, toe: 'Toe'):
        self.parts = []
        self.junction: CONDITION_JUNCTION = CONDITION_JUNCTION.junction_none
        self.toe = toe

    def process_tree(self):
        if self.junction == CONDITION_JUNCTION.junction_and:
            return self.process_and_tree()
        elif self.junction == CONDITION_JUNCTION.junction_or:
            return self.process_or_tree()
        else:
            raise ToeInvalidConditionException()

    def process_and_tree(self):
        result = True
        for part in self.parts:
            if not self.toe.process_condition(part):
                result = False
                break
        return result

    def process_or_tree(self):
        result = False
        for part in self.parts:
            if self.toe.process_condition(part):
                result = True
                break
        return result


class CompoundConditionParsingInfo:
    def __init__(self, toe: 'Toe'):
        self.top_tree: ConditionTree = ConditionTree(toe=toe)
        self.current_tree = self.top_tree
        self.i = 0
        self.current_depth = 0
        self.in_string = False
        self.string_quote = ""
        self.condition_start = 0


class CONDITION_JUNCTION(enum.Enum):
    junction_none = -1
    junction_or = 0
    junction_and = 1

class ReturnToChildScope:
    def __init__(self, name):
        self.name = name


class VariableScope:
    variables = {}
    parent_scope = None

    def __init__(self, variable_dict, parent_scope=None):
        self.variables = variable_dict if variable_dict is not None else {}
        self.parent_scope = parent_scope

    def find_variable(self, variable_name, passed_names=None, original_scope: 'VariableScope'=None):
        if passed_names is not None:
            names = passed_names
        else:
            names = self.get_names(variable_name=variable_name, passed_names=passed_names)

        if len(names) > 0 and self.is_variable(variable_name=names[0], original_scope=original_scope):
            if len(names) > 0:
                if names[0] in self.variables:
                    res = self.variables.get(names[0])
                elif self.parent_scope is not None:
                    res = self.parent_scope.find_variable(names[0], names, self if original_scope is None else original_scope)
                else:
                    return None
                if (type(res) is list and len(res) > 0) or type(res) is dict:
                    for i in range(1, len(names)):
                        if ((names[i][0] == "'" and names[i][-1] == "'") or (names[i][0] == "\"" and names[i][-1] == "\"")) \
                                and names[i].find("+") == -1:
                            resolved_name = names[i][1: -1]
                        else:
                            try:
                                resolved_name = int(names[i])
                            except:
                                resolved_name = self.find_variable(names[i], original_scope=original_scope)
                        if resolved_name in res or (resolved_name is int and len(res) > resolved_name and res[resolved_name] is not None):
                            res = res[resolved_name]
                        elif original_scope is not None:
                            return original_scope.find_variable(variable_name=variable_name)
                        else:
                            return None
                return res
            else:
                return self.variables[names[0]]

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

    def is_variable(self, variable_name, passed_names=None, original_scope=None):
        names = self.get_names(variable_name=variable_name, passed_names=passed_names)

        if self.variables.get(names[0]) is not None:
            if len(names) > 0:
                if names[0] in self.variables:
                    res = self.variables.get(names[0])
                elif self.parent_scope is not None:
                    res = self.parent_scope.is_variable(names[0], names, self if original_scope is None else original_scope)
                else:
                    return None
                if type(res) is list or type(res) is dict:
                    for i in range(1, len(names)):
                        if ((names[i][0] == "'" and names[i][-1] == "'") or (names[i][0] == "\"" and names[i][-1] == "\"")) \
                                and names[i].find("+") == -1:
                            resolved_name = names[i][1: -1]
                        else:
                            return self.is_variable(names[i], original_scope=original_scope)
                        if resolved_name in res:
                            return True
                        elif original_scope is not None:
                            return original_scope.is_variable(variable_name=variable_name)
                        else:
                            return None
                return res is not None
            else:
                return True

        if self.parent_scope is None:
            return False
        if self.parent_scope.is_variable(variable_name, names):
            return True
        return False

    def get_names(self, variable_name, passed_names):
        names = [] if passed_names is None else passed_names
        if passed_names is None and variable_name.find("['") > -1:
            j = variable_name.find("[")
            names = [variable_name[:j], ]
            j += 1
            level = 1
            temp = ""
            while j < len(variable_name):
                if variable_name[j] == "[":
                    if level == 0:
                        names.append(temp)
                        temp = ""
                    else:
                        temp += variable_name[j]
                    level += 1
                elif variable_name[j] == "]":
                    if level > 1:
                        temp += variable_name[j]
                    level -= 1
                else:
                    temp += variable_name[j]
                j += 1
                if j < len(variable_name) and level == -1:
                    return None
            names.append(temp)
        else:
            return [variable_name]
        return names

    def is_variable_in_current_scope(self, variable_name):
        return self.variables.get(variable_name) is not None
