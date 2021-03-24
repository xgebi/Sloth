import os
import re
import uuid

from app.toes.node import Node
from app.toes.root_node import RootNode
from app.toes.xml_parser import XMLParser


def render_toe(*args, template, path_to_templates, data=None, **kwargs):
    if path_to_templates is None:
        return None

    toe_engine = Toe(path_to_templates, template, data=data, **kwargs)
    return toe_engine.process_tree()


class Toe:
    tree: RootNode = None
    new_tree: RootNode = None
    path_to_templates = ""
    template_load_error = False
    variables = None
    current_scope = None
    later_replacement = {}

    def __init__(self, path_to_templates, template, data=None, **kwargs):
        self.path_to_templates = path_to_templates
        self.variables = Variable_Scope(data, None)
        self.current_scope = self.variables

        self.new_tree = RootNode(html=True)
        self.new_tree.children.append(
            Node(
                name='html',
                parent=self.new_tree
            )
        )

        for node in self.new_tree.children:
            if node.type == Node.NODE:
                lang = self.current_scope.find_variable('lang')
                node.set_attribute(name='lang', value=lang if lang is not None else 'en')

        xp = XMLParser(path=(os.path.join(path_to_templates, template)))
        self.tree = xp.parse_file()

    def process_tree(self):
        # There can only be one root element
        if len(self.tree.children) != 1:
            return None

        for node in self.tree.children[0].children:
            res = self.process_subtree(self.new_tree.children[0], node)

            if res is not None:
                self.new_tree.childNodes[1].appendChild(res)
        xml_str = self.new_tree.toxml()[self.new_tree.toxml().find('?>') + 2:]
        for key in self.later_replacement.keys():
            xml_str = xml_str.replace(key, self.later_replacement[key])

        return xml_str

    def process_subtree(self, new_tree_parent: Node, tree: Node):
        """
		Params:
			new_tree_parent: Document or Node object
			tree: Document or Node object
		Returns
			Document or Node object
		"""
        if tree.type == Node.TEXT:
            return self.new_tree.createTextNode(tree.wholeText)

        # check for toe tags
        if tree.get_name().startswith('toe:'):
            return self.process_toe_tag(new_tree_parent, tree)

        # check for toe attributes
        attributes = tree.attributes.keys()
        for attribute in attributes:
            if attribute == 'toe:if':
                return self.process_if_attribute(new_tree_parent, tree)
            if attribute == 'toe:for':
                return self.process_for_attribute(new_tree_parent, tree)
            if attribute == 'toe:while':
                return self.process_while_attribute(new_tree_parent, tree)

        # append regular element to parent element
        new_tree_node = self.new_tree.children.append(Node(name=tree.get_name()))
        content_set = False
        if tree.attributes is not None or len(tree.attributes) > 0:
            for key in tree.attributes.keys():
                if key == 'toe:value':
                    self.process_toe_value_attribute(tree, new_tree_node)
                elif key.startswith('toe:attr'):
                    self.process_toe_attr_attribute(tree, new_tree_node, key)
                elif key == 'toe:content':
                    content_set = True
                    self.process_toe_content_attribute(tree, new_tree_node)
                else:
                    new_tree_node.set_attribute(key, tree.getAttribute(key))
        if not content_set:
            for node in tree.children:
                res = self.process_subtree(new_tree_node, node)

                if type(res) is list:
                    for temp_node in res:
                        if len(new_tree_node.children) > 0 \
                                and new_tree_node.children[-1].type == Node.TEXT:
                            # TODO look at replaceWholeText
                            new_tree_node.childNodes[-1].replaceWholeText(new_tree_node.childNodes[-1].wholeText + " ")
                        new_tree_node.children.append(temp_node)
                if res is not None:
                    if len(new_tree_node.childNodes) > 0 and new_tree_node.childNodes[-1].nodeType == Node.TEXT_NODE:
                        new_tree_node.childNodes[-1].replaceWholeText(new_tree_node.childNodes[-1].wholeText + " ")
                    if type(res) is list:
                        for thing in res:
                            new_tree_node.appendChild(thing)
                    else:
                        new_tree_node.appendChild(res)

        return new_tree_node

    def process_toe_tag(self, parent_element: Node, element: Node):
        # TODO toe:fragment condition

        if len(element.get_attribute('toe:if')) > 0:
            if not self.process_condition(element.get_attribute('toe:if'))["value"]:
                return None

        if element.get_name().startswith("toe:fragment"):
            pass

        if element.get_name().find('import') > -1:
            return self.process_toe_import_tag(parent_element, element)

        if element.get_name().find('assign') > -1:
            return self.process_assign_tag(element)

        if element.get_name().find('create') > -1:
            return self.process_create_tag(element)

        if element.get_name().find('modify') > -1:
            return self.process_modify_tag(element)

    def process_toe_import_tag(self, parent_element, element):
        file_name = element.getAttribute('file')

        imported_tree = {}

        if file_name.endswith(".toe.html") or file_name.endswith(".toe.xml"):
            xp = XMLParser(path=os.path.join(self.path_to_templates, file_name))
            imported_tree = xp.parse_file()
            # TODO continue here
            top_node = self.new_tree.createElement(imported_tree.childNodes[0].childNodes[0].tagName)
            for child_node in imported_tree.childNodes[0].childNodes[0].childNodes:
                new_node = self.process_subtree(top_node, child_node)
                if len(top_node.childNodes) >= 1 and top_node.childNodes[-1].nodeType == Node.TEXT_NODE:
                    top_node.childNodes[-1].replaceWholeText(top_node.childNodes[-1].wholeText + " ")
                if new_node is not None:
                    top_node.appendChild(new_node)
            return top_node
        return None

    # toe:value="value"
    def process_toe_value_attribute(self, tree, new_node):
        value = tree.getAttribute("toe:value")

        try:
            value_int = int(value)
            value_float = float(value)

            if value_int == value_float:
                new_node.setAttribute("value", value_int)
            else:
                new_node.setAttribute("value", value_float)
        except ValueError:
            if re.search(r"[ ]?\+[ ]?", value) is None:
                if type(value) == str and value[0] == "'":
                    new_node.setAttribute("value", value[1: len(value) - 1])
                else:
                    resolved_value = self.current_scope.find_variable(value)
                    if resolved_value is not None:
                        new_node.setAttribute("value", resolved_value)
            else:
                var_arr = re.split(r"[ ]?\+[ ]?", value)
                if var_arr is None:
                    return
                result = ""
                for item in var_arr:
                    if item[0] == "'":
                        result += item[1: len(item) - 1]
                    else:
                        resolved_value = self.current_scope.find_variable(item)
                        result += resolved_value if resolved_value is not None else ""

                new_node.setAttribute("value", result)

    # toe:attr-[attribute name]="value"
    def process_toe_attr_attribute(self, tree, new_node, key):
        new_key = key[key.find("-") + 1:]
        value = tree.getAttribute(key)

        try:
            value_int = int(value)
            value_float = float(value)

            if value_int == value_float:
                new_node.setAttribute(new_key, value_int)
            else:
                new_node.setAttribute(new_key, value_float)
        except ValueError:
            if re.search(r"[ ]?\+[ ]?", value) is None:
                if type(value) == str and value[0] == "'":
                    new_node.setAttribute(new_key, value[1: len(value) - 1])
                else:
                    resolved_value = self.current_scope.find_variable(value)
                    if resolved_value is not None:
                        new_node.setAttribute(new_key, resolved_value)
            else:
                var_arr = re.split(r"[ ]?\+[ ]?", value)
                if var_arr is None:
                    return
                result = ""
                for item in var_arr:
                    if item[0] == "'":
                        result += item[1: len(item) - 1]
                    else:
                        resolved_value = self.current_scope.find_variable(item)
                        result += resolved_value if resolved_value is not None else ""

                new_node.setAttribute(new_key, result)

    # toe:content="value"
    def process_toe_content_attribute(self, tree, new_node):
        value = tree.getAttribute("toe:content")

        try:
            value_int = int(value)
            value_float = float(value)

            if value_int == value_float:
                new_node.appendChild(self.new_tree.createTextNode(str(value_int)))
            else:
                new_node.appendChild(self.new_tree.createTextNode(str(value_float)))
        except ValueError:
            if re.search(r"[ ]?\+[ ]?", value) is None:
                if type(value) == str and value[0] == "'":
                    new_node.appendChild(self.new_tree.createTextNode(value[1: len(value) - 1]))
                else:
                    resolved_value = self.current_scope.find_variable(value)
                    resolved_id = str(uuid.uuid4())
                    if resolved_value is not None:
                        self.later_replacement[resolved_id] = resolved_value
                        new_node.appendChild(self.new_tree.createTextNode(resolved_id))
                    else:
                        new_node.appendChild(self.new_tree.createTextNode(
                            str(tree.childNodes[0].wholeText) if tree.childNodes[0].nodeType == Node.TEXT_NODE else ""))
            else:
                var_arr = re.split(r"[ ]?\+[ ]?", value)
                if var_arr is None:
                    return
                result = ""
                for item in var_arr:
                    if item[0] == "'":
                        result += item[1: len(item) - 1]
                    else:
                        resolved_value = self.current_scope.find_variable(item)
                        result += resolved_value if resolved_value is not None else ""
                result_id = str(uuid.uuid4())
                self.later_replacement[result_id] = result
                new_node.appendChild(self.new_tree.createTextNode(result_id))

    def process_assign_tag(self, element):
        var_name = element.getAttribute('var')
        var_value = element.getAttribute('value')

        if var_name is None or len(var_name) == 0:
            raise ValueError('Variable cannot have no name')

        variable = self.current_scope.find_variable(var_name)
        if variable is None:
            raise ValueError('Variable doesn\'t exist')

        self.current_scope.assign_variable(var_name, var_value)
        return None

    def process_create_tag(self, element):
        var_name = element.getAttribute('var')
        var_value = element.getAttribute('value')

        if var_name is None or len(var_name) == 0:
            raise ValueError('Variable cannot have no name')

        if self.current_scope.is_variable_in_current_scope(var_name):
            raise ValueError('Variable cannot be created twice')

        self.current_scope.variables[var_name] = var_value
        return None

    def process_modify_tag(self, element):
        var_name = element.getAttribute('var')
        var_value = element.getAttribute('value')

        if var_name is None or len(var_name) == 0:
            raise ValueError('Variable cannot have no name')

        variable = self.current_scope.find_variable(var_name)
        if variable is None:
            raise ValueError('Variable doesn\'t exist')

        if element.hasAttribute('toe:inc'):
            if type(variable) == int or type(variable) == float:
                self.current_scope.assign_variable(var_name, variable + 1)
                return None

        if element.hasAttribute('toe:dec'):
            if type(variable) == int or type(variable) == float:
                self.current_scope.assign_variable(var_name, variable - 1)
                return None

        if element.hasAttribute('toe:add'):
            if (type(variable) == int or type(variable) == float):
                self.current_scope.assign_variable(var_name, variable + float(element.getAttribute('toe:add')))
                return None

        if element.hasAttribute('toe:sub'):
            if (type(variable) == int or type(variable) == float):
                self.current_scope.assign_variable(var_name, variable - float(element.getAttribute('toe:sub')))
                return None

        if element.hasAttribute('toe:mul'):
            if (type(variable) == int or type(variable) == float):
                self.current_scope.assign_variable(var_name, variable * float(element.getAttribute('toe:mul')))
                return None

        if element.hasAttribute('toe:div'):
            if (type(variable) == int or type(variable) == float):
                if (float(element.getAttribute('toe:div')) != 0):
                    self.current_scope.assign_variable(var_name, variable / float(element.getAttribute('toe:div')))
                    return None
                raise ZeroDivisionError()

        if element.hasAttribute('toe:mod'):
            if (type(variable) == int or type(variable) == float):
                if (float(element.getAttribute('toe:mod')) != 0):
                    if (float(element.getAttribute('toe:mod')) != 0):
                        self.current_scope.assign_variable(var_name, variable % float(element.getAttribute('toe:mod')))
                    return None
                raise ZeroDivisionError()

        if element.hasAttribute('toe:pow'):
            if (type(variable) == int or type(variable) == float):
                self.current_scope.assign_variable(var_name, variable ** float(element.getAttribute('toe:pow')))
                return None

        return None

    def process_if_attribute(self, parent_element, element):
        if not self.process_condition(element.getAttribute('toe:if')):
            return None
        element.removeAttribute('toe:if')
        return self.process_subtree(parent_element, element)

    def process_for_attribute(self, parent_element, element):
        result_nodes = []
        # get toe:for attribute
        iterable_cond = element.getAttribute('toe:for')
        # split string between " in "
        items = iterable_cond.split(" in ")
        # find variable on the right side
        # create python for loop
        iterable_item = self.current_scope.find_variable(items[1])
        if iterable_item is None:
            return None

        element.removeAttribute('toe:for')

        for thing in iterable_item:
            # local scope creation
            local_scope = Variable_Scope({}, self.current_scope)
            self.current_scope = local_scope

            self.current_scope.variables[items[0]] = thing

            # process subtree
            result_node = self.process_subtree(parent_element, element)
            if result_node is not None:
                result_nodes.append(result_node)

            # local scope destruction
            self.current_scope = self.current_scope.parent_scope
            local_scope = None
        return result_nodes

    def process_while_attribute(self, parent_element, element):
        result_nodes = []
        # get toe:for attribute
        iterable_cond = element.getAttribute('toe:while')

        contains_condition = False
        for cond in (" gt ", " gte ", " lt ", " lte ", " eq ", " neq "):
            if cond in iterable_cond:
                contains_condition = True
                break

        if not contains_condition:
            return None

        element.removeAttribute('toe:while')

        while self.process_condition(iterable_cond):
            # local scope creation
            local_scope = Variable_Scope({}, self.current_scope)
            self.current_scope = local_scope

            # process subtree
            result_node = self.process_subtree(parent_element, element)
            if result_node is not None:
                result_nodes.append(result_node)

            # local scope destruction
            self.current_scope = self.current_scope.parent_scope
            local_scope = None

        return result_nodes

    def process_condition(self, condition):
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

        if (condition["value"].count("and") > 0 or condition["value"].count("or") > 0):
            return False

        # split condition["value"] by " xxx? "
        sides = re.split(" [a-z][a-z][a-z]? ", condition["value"])
        # at least one side has to be a variable
        if len(sides) != 2:
            return False

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
            return resolved[0] >= resolved[1]
        if " gt " in condition["value"]:
            return resolved[0] > resolved[1]
        if " lte " in condition["value"]:
            return resolved[0] <= resolved[1]
        if " lt " in condition["value"]:
            return resolved[0] < resolved[1]
        if " neq " in condition["value"]:
            return resolved[0] != resolved[1]
        if " eq " in condition["value"]:
            return resolved[0] == resolved[1]
        return False

    # Adapted from https://stackoverflow.com/a/16919069/6588356
    def remove_blanks(self, node):
        for x in node.childNodes:
            if x.nodeType == Node.TEXT_NODE:
                if x.nodeValue:
                    x.nodeValue = x.nodeValue.strip()
            elif x.nodeType == Node.ELEMENT_NODE:
                self.remove_blanks(x)


class Variable_Scope:
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
                res = self.variables[names[0]]
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
