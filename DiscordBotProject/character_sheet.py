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

    def data_curry(self, function, key):
        return function(self.data[key])

    def save_to_file(self, filepath):
        save_file(filepath, self.data)
