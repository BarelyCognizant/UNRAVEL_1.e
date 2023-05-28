import re
import json


# Utils
def str_to_list(value):
    return list(map(lambda x: x[1:-1], re.findall("\".*?\"", value)))


def str_to_dict(value):
    value = re.sub("\s", "", value)
    values = re.findall("\".*?\"\s*\:\s*[0-9]+", value)
    ret = {}
    list(map(lambda x: ret.update({x[0]: x[1]}), map(lambda y: (
        re.findall("(?<=\").*(?=\")", y)[0], int(re.findall("(?<=\:)[0-9]*", re.sub("\s", "", y))[0])), values)))
    return ret


def dic_to_list(dictionary):
    ret = []
    for v in dictionary:
        ret.append("{name} ({val})".format(name=v, val=dictionary[v]))
    return ret


def fold_string(string_list, cons):
    if len(string_list) > 0:
        ret = string_list[0]
        for s in string_list[1:]:
            ret = ret + cons + s
    else:
        ret = ""
    return ret


def load_file(filepath):
    with open(filepath) as json_file:
        return json.load(json_file)


class Player:
    # attributes are either "string", "int", "[string]", "{string:dictionary}"
    # names are any string
    # values are ints or strings
    # operators are "+", "-", "="
    # names must be unique

    # TODO: save to JSON (should be easy)
    # load from JSON (less easy)

    # in format {name:(type, value)}
    data = {}

    def __init__(self, data=None):
        if data is None:
            self.data = {}
            self.change_attribute(operation="add", name="Name", value=None, attr_type="string")
            self.change_attribute(operation="add", name="HP", value=None, attr_type="int")
            self.change_attribute(operation="add", name="Skills", value=None, attr_type="{string:int}")
            self.change_attribute(operation="add", name="Inventory", value=None, attr_type="{string:int}")
            self.change_attribute(operation="add", name="Achievements", value=None, attr_type="[string]")
        else:
            self.data = data

    def save_file(self, filepath):
        with open(filepath, 'w') as fp:
            json.dump(self.data, fp)

    def change_attribute(self, *, operation=None, name=None, value=None, attr_type=None):
        name = fold_string(list(map(lambda a: a.capitalize(), re.split("\s", name))), "_")
        if operation == "add":
            if attr_type == None and value == None:
                return "at least one of type or initial value must be specified"
            if attr_type == None:
                if re.search("\{.+\:[0-9]+(\,\s*.+\:[0-9]+)*}", value):
                    attr_type = "{string:int}"
                elif re.search("\[\s*\".*\"\s*(\,\s*\".*\"\s*)*]", value):
                    attr_type = "[string]"
                elif value.isdigit():
                    attr_type = "int"
                else:
                    attr_type = "string"
            return self.add_attribute(name, attr_type, value)
        elif operation == "remove":
            return self.delAttribute(name)

    def add_attribute(self, name, attr_type, value=None):
        if name in self.data:
            return "cannot add attribute {name} because it already exists".format(name=name)
        elif value == None:
            if attr_type == "string":
                self.data.update({name: (attr_type, "")})
            elif attr_type == "int":
                self.data.update({name: (attr_type, 0)})
            elif attr_type == "[string]":
                self.data.update({name: (attr_type, [])})
            elif attr_type == "{string:int}":
                self.data.update({name: (attr_type, {})})
        else:
            if attr_type == "[string]":
                if re.search("\[\s*\".*\"\s*(\,\s*\".*\"\s*)*]", value):
                    self.data.update({name: (attr_type, str2list(value))})
                else:
                    return "cannot convert {value} to type [string]".format(value=value)
            elif attr_type == "{string:int}":
                if re.search("\{.+\:[0-9]+(\,\s*.+\:[0-9]+)*}", value):
                    self.data.update({name: (attr_type, str2dict(value))})
                else:
                    return "cannot convert {value} to type int".format(value=value)
            elif attr_type == "int":
                if value.isdigit():
                    self.data.update({name: (attr_type, int(value))})
                else:
                    return "cannot convert {value} to type int".format(value=value)
            elif attr_type == "string":
                self.data.update({name: (attr_type, value)})
            else:
                return "attribute type of {value} ({attr_type}) is invalid attribute type must be in the string, int, [string], or \{string:int\}".format(
                    value=value, attr_type=attr_type)
        return "added attribute {name} with type {attr_type} and value {value}".format(name=name, attr_type=attr_type,
                                                                                       value=value)

    def delAttribute(self, name):
        if name not in self.data:
            return "cannot delete attribute {name} because it doesn't exist".format(name=name)
        else:
            del self.data[name]
            return "deleted attribute {name}".format(name=name)

    # returns a string to be sent in response as a character sheet
    def get_player_desc(self):
        int_vals = ""
        str_vals = ""
        skills = ""
        inventory = ""
        achievements = ""
        str_lists = ""
        dicts = ""
        ret = ""
        if "name" in self.data:
            str_vals = str_vals + "Name: " + self.data["name"][1]

        for k in self.data:
            if k not in ["name", "skills", "inventory", "achievements"]:
                # handle data of type int
                if self.data[k][0] == "int":
                    int_vals = int_vals + "\n" + "{name}: {value}".format(name=k, value=self.data[k][1])
                # handle data of type string
                elif self.data[k][0] == "string":
                    str_vals = str_vals + "\n" + "{name}: {value}".format(name=k, value=self.data[k][1])
                # handle data of type [string]
                elif self.data[k][0] == "[string]":
                    str_lists = str_lists + k + "\n  " + fold_string(list(self.data[k][1]), "\n  ") + "\n"
                # handle data of type {string:int}
                elif self.data[k][0] == "{string:int}":
                    dicts = dicts + "\n" + k + ":"
                    dicts_list = dic_to_list(self.data[k][1])
                    for s in dicts_list:
                        dicts = dicts + "\n  " + s
        int_vals = int_vals[1:]

        if "skills" in self.data:
            skills = "Skills:"
            skills_list = dic_to_list(self.data["skills"][1])
            for s in skills_list:
                skills = skills + "\n  " + s

        if "inventory" in self.data:
            inventory = "Inventory:"
            inventory_list = dic_to_list(self.data["inventory"][1])
            for s in inventory_list:
                inventory = inventory + "\n  " + s

        if "achievements" in self.data:
            achievements = "Achievements:\n  "
            if len(self.data["achievements"][1]) > 0:
                achievements = achievements + fold_string(self.data["achievements"][1], "\n  ") + "\n"
            # achievements = achievements[:-3]
        ret = fold_string(
            list(filter(lambda x: x != "", [str_vals, int_vals, skills, inventory, achievements, str_lists, dicts])),
            "\n")
        ret = re.sub("(\n\s*){2,}", "\n", ret)
        return "```\n" + ret + "```"

    # returns a string, either confirming success, or an error message. to send as response to the triggering command
    def change_data(self, name, operator, value="", key=""):
        name = fold_string(list(map(lambda a: a.capitalize(), re.split("\s", name))), "_")
        if name not in self.data:
            return "no such attribute in character sheet {name}".format(name=name)
        ret = ""
        cur_data = self.data[name]
        cur_type = cur_data[0]
        cur_val = cur_data[1]
        val_type = type(value)

        # catch invalid operators
        if operator not in ["+", "-", "="]:
            return "the operator {op} was invalid, it must be +, -, or =".format(op=operator)

        if cur_type in ["string", "[string]"]:
            value = str(value)
        elif cur_type in ["int", "{string:int}"]:
            if value.isdigit():
                value = int(value)
            else:
                value = str2dict(value)

        # match type of specified target, and inputted type
        if cur_type == "string":
            if operator != "=":
                ret = "could not set {name} to {val} because operator {op} was invalid, only the = operator can be applied to strings".format(
                    name=name, val=value, op=operator)
            else:
                self.data.update({name: ("string", value)})
                ret = "set value of {name} to {val}".format(name=name, val=value)
        if cur_type == "[string]":
            if operator == "+":
                self.data.update({name: ("[string]", cur_val + [value])})
                ret = "appended {val} onto {name}".format(name=name, val=value)
            elif operator == "-":
                self.data[name][1].remove(value)
                ret = "removed {val} from {name}".format(name=name, val=value)
            elif operator == "=":
                ret = "unable to set {name} to {val} because = operator cannot be applied to [string]".format(name=name,
                                                                                                              val=value)
        elif cur_type == "int":
            if operator == "+":
                self.data.update({name: ("int", cur_val + value)})
                up_val = cur_val + value
            elif operator == "-":
                self.data.update({name: ("int", cur_val - value)})
                up_val = cur_val - value
            elif operator == "=":
                self.data.update({name: ("int", value)})
                up_val = value
            ret = "appended {val} to {name}, new value is {up_val}".format(name=name, val=value, up_val=cur_val + value)
        elif cur_type == "{string:int}":
            if operator == "+":
                for k in value:
                    if k in cur_val:
                        new_val = cur_val[k] + value[k]
                        cur_val.update({k: new_val})
                        ret = "updated {name} at {key} with {val}, new value is {up_val}".format(name=name, val=value,
                                                                                                 up_val=cur_val,
                                                                                                 key=key)
                    else:
                        cur_val.update({k: value[k]})
                        ret = "updated {name} to add {key} with value {val}".format(name=name, val=value, key=key)
                    self.data.update({name: ("{string:int}", cur_val)})
            elif operator == "-":
                for k in value:
                    if k in cur_val:
                        new_val = cur_val[k] - value[k]
                        if new_val == 0:
                            del cur_val[k]
                        else:
                            cur_val.update({k: new_val})
                            ret = "updated {name} at {key} to subtract {val}, new value is {up_val}".format(name=name,
                                                                                                            val=value,
                                                                                                            up_val=cur_val,
                                                                                                            key=key)
                    else:
                        return "cannot subtract from a {n} that doesn't exist".format(n=name)
                    self.data.update({name: ("{string:int}", cur_val)})
        return ret