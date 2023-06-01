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


def save_file(filepath, sheet):
    with open(filepath, 'w') as f:
        json.dump(sheet, f)


class Character:
    # valid data types: [str, int, dict, list]
    def __init__(self, player=None, name="", skill_list=None, HP=5, filepath=""):
        self.data = {}
        if not filepath == "":
            self.data.update(load_file(filepath))
        else:
            if skill_list is None:
                skill_list = []
            skills = {}
            if len(skill_list) > 0:
                for i in range(len(skill_list)):
                    skills[skill_list[i]] = max(5 - i, 2)
            self.data.update({
                "Name": name,
                "Player": player,
                "HP": HP,
                "Inventory": {},
                "Skills": skills,
                "Titles": {},
                "Achievements": {},
            })

    def remove_data(self, target, key):
        if target is not None:
            try:
                data_source, data_path = self.find_data(target)
            except RuntimeError as e:
                return e
        else:
            data_source = self.data
        return data_source.pop(key)

    def add_data(self, target, key, value):
        if target is not None:
            try:
                data_source, data_path = self.find_data(target)
            except RuntimeError as e:
                return e
        else:
            data_source = self.data
        if type(data_source[key]) is int:
            if type(value) is int:
                data_source.update({key: data_source[key] + value})
            else:
                data_source.update({key: value})
            return "adding " + str(key) + " (" + str(value) + "). new value: " + str(key) + " (" + str(
                data_source[key]) + ")"
        elif type(data_source[key]) is list:
            data_source[key].append(value)
            return "adding " + str(key) + " [" + str(value) + "]. new value: " + str(key) + str(
                data_source[key])
        elif type(data_source[key]) is dict:
            if type(value) is dict:
                data_source[key].update(value)
            elif value not in data_source[key]:
                data_source[key].update({value: 1})
            else:
                return self.add_data(target=(target + "/key"), key=value, value=1)
        else:
            ret = "overwriting \n" + self.get_desc(key=key, value=data_source[key])
            data_source.update({key: value})
            return ret + "\nwith\n" + self.get_desc(key=key, value=value)

    def find_data(self, target):
        if target is not None:
            data_path = re.split("/", target)
            source = self.data
            for s in data_path:
                if s in source:
                    source = source[s]
                else:
                    raise RuntimeError("data path " + target + " failed to find " + s)
            return source, data_path
        else:
            raise RuntimeError("data path is None")

    def get_data(self, target=None, key=None):
        if key is None:
            return self.find_data(target)[0]
        else:
            return self.find_data(target)[0][key]

    def save_to_file(self, filepath):
        save_file(filepath, self.data)

    def get_desc(self, key=None, value=None, initial_indent="", output="", simple_style="colon"):
        indent = ""
        output = ""

        def append(string):
            return output + initial_indent + indent + string

        if value is None:
            value = self.data

        recur = []
        if type(value) == int or type(value) == str:
            if key is None:
                return append(str(value)) + "\n"
            elif simple_style == "colon":
                return append(str(key) + ": " + str(value)) + "\n"
            elif simple_style == "paren":
                return append(str(key) + "(" + str(value) + ")") + "\n"

        elif type(value) == list:
            if key is not None:
                output = append(str(key)) + ":\n"
            for v in value:
                output = output + self.get_desc(value=v, initial_indent=initial_indent + "  ")
        elif type(value) == dict:
            if key is not None:
                output = append(str(key)) + ":\n"
            for k, v in value.items():
                output = append(self.get_desc(key=k, value=v, initial_indent=initial_indent + "  "))
        return output
