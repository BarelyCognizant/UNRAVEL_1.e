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


def save_file(filepath, dict):
    with open(filepath, 'w') as f:
        json.dump(dict, f)


class Player:
    data = {}

    def __init__(self, name="", HP=0, filepath=""):
        self.data = {}
        if filepath == "":
            self.data.update(load_file(filepath))
        else:
            self.data.update({
                "name": name,
                "HP": HP
            })

    def update_data(self, update):
        self.data.update(update)

    def get_data(self, key=None):
        if key is None:
            return self.data
        else:
            if key in self.data:
                return self.data[key]
            else:
                return None

    def save_to_file(self, filepath):
        save_file(filepath, self.data)

    def get_desc(self, key=None, value=None, initial_indent="", output="", simple_style="colon"):
        indent = ""
        output = ""

        def append(string):
            return output + initial_indent + indent + string + "\n"

        if value is None:
            value = self.data

        recur = []
        if type(value) == int or type(value) == str:
            if key is None:
                return append(value)
            elif simple_style == "colon":
                return append(key + ": " + value)
            elif simple_style == "paren":
                return append(key + "(" + value + ")")

        elif type(value) == list:
            if key is not None:
                output = append(key)
            for v in value:
                output = output + self.get_desc(value=v, initial_indent=initial_indent + "  ")
        elif type(value) == tuple:
            output = output + self.get_desc(key=value[0], value=value[1])
        elif type(value) == dict:
            if key is not None:
                output = append(key)
            for k, v in value.items():
                output = append(self.get_desc(key=k, value=v))
        return output
