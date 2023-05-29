gremlins = []
online_gremlins = []


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
