import os
from character_sheet import save_file, load_file

gremlins = []
online_gremlins = []
message_shortcuts = {"test": "This is an Automated Server Test Message. \n Please Ignore."}
path = "./Backups/Server/messages.json"


def login_gremlin(name):
    online_gremlins.append(name)
    return "Server Update: Server online at " + str(len(online_gremlins)) + "/" + str(len(gremlins)) + " capacity."


def logout_gremlin(name):
    online_gremlins.remove(name)
    if len(online_gremlins) > 0:
        return "Server Update: Server online at " + str(len(online_gremlins)) + "/" + str(len(gremlins)) + " capacity."
    else:
        return "Server Update: Server is going offline."


def load_gremlins(gremlin_list):
    gremlins.append(gremlin_list)


def command_wrap(text):
    return "```" + text + "```"


def message(text):
    if text in message_shortcuts:
        server_message = message_shortcuts[text]
    else:
        server_message = text
    return command_wrap(server_message)


def add_message(name, text):
    message_shortcuts[name] = text
    save_file(path, message_shortcuts)


def remove_message(name):
    message_shortcuts.pop(name)
    save_file(path, message_shortcuts)


def load_messages():
    global message_shortcuts
    if os.path.exists(path):
        message_shortcuts = load_file(path)
