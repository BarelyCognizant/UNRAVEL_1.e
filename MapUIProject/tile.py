import utils


class Tile:
    loc = (0, 0)
    id = 0
    type = ""
    color = utils.colors["forest"]

    def __init__(self, location, type, unique_id=0, neighbours=[]):
        self.loc = location
        self.id = unique_id
        self.type = type
        self.neighbours = neighbours
        self.color = utils.colors[self.type]

    def render(self, surface, camera, focus=False):
        x = self.loc[0]
        y = self.loc[1]
        color = self.color[0]
        if focus:
            color = self.color[1]
        bounds = utils.drawCell(surface, camera, x, y, color)
        return bounds

    def add_neighbour(self, neighbour):
        self.neighbours.append(neighbour)
