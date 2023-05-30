import pygame
import utils as utils


class Tile:
    loc = (0, 0)
    id = 0
    type = ""
    color = None
    neighbours = []
    label = ""
    comments = ""
    covered = False
    height = 0

    def __init__(self, location, type, unique_id=0, label="", comments=""):
        self.loc = location
        self.id = unique_id
        self.type = type
        self.color = utils.colors[self.type.split("\\")[0]]
        self.label = label
        self.comments = comments
        self.covered = utils.metadata[type]["covered"]
        self.height = utils.metadata[type]["height"]
        self.visible = False
        self.distance = -1
        self.neighbours = []

    def render(self, surface, camera, focus=False):
        x = self.loc[0]
        y = self.loc[1]
        if utils.vertical:
            color = self.color[0]
            if focus:
                color = self.color[1]
            bounds = utils.drawCell(surface, camera, x, y, color)
        else:
            image = pygame.image.load("..\\MapUIProject\\tiles\\used\\" + self.type)
            if focus:
                brighten = 30
                image.fill((brighten, brighten, brighten), special_flags=pygame.BLEND_RGB_ADD)
            bounds = utils.drawTile(surface, camera, x, y, image)
        return bounds

    def renderLabels(self, surface, camera):
        x = self.loc[0]
        y = self.loc[1]
        if self.label != "":
            utils.drawLabel(surface, camera, x, y, self.label)

    def get_bounds(self, camera):
        x = self.loc[0]
        y = self.loc[1]
        return utils.getBounds(camera, x, y)

    def add_neighbour(self, neighbour):
        self.neighbours.append(neighbour)
