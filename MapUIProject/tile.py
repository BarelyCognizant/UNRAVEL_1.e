import random

import pygame
import utils as utils
import math


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
    remembered = False
    rType = ""
    rLabel = ""
    weather = 0.0
    cloudPoints = []

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
        bounds = []
        if utils.vertical:
            color = self.color[0]
            if focus:
                color = self.color[1]
            if self.visible:
                bounds = utils.drawCell(surface, camera, x, y, color)
        else:
            if self.visible:
                image = pygame.image.load("..\\MapUIProject\\tiles\\used\\" + self.type)
                if focus:
                    brighten = 30
                    image.fill((brighten, brighten, brighten), special_flags=pygame.BLEND_RGB_ADD)
                bounds = utils.drawTile(surface, camera, x, y, image)
            elif self.remembered:
                image = pygame.image.load("..\\MapUIProject\\tiles\\used\\" + self.rType)
                image = utils.convertToGreyscale(image)
                bounds = utils.drawTile(surface, camera, x, y, image)

        return bounds

    def setWeather(self, weatherValue):
        if weatherValue < -0.2:
            if self.type.split("\\")[0] == "snow":
                self.weather = "SNOW"
            else:
                self.weather = "RAIN"
        elif weatherValue < -0.05:
            self.weather = "CLOUD"
        else:
            self.weather = "CLEAR"

    def renderWeather(self, surface, camera):
        for point in self.cloudPoints:
            x = point[0]
            y = point[1]
            r = math.floor(random.random() * 3.0)
            image = pygame.image.load(utils.dryClouds[r])
            image.fill((255, 255, 255, 150 + (random.random() * 100.0)), special_flags=pygame.BLEND_RGBA_MIN)
            if self.visible:
                if self.weather == "SNOW":
                    brighten = 100
                    image.fill((brighten, brighten, brighten), special_flags=pygame.BLEND_RGB_SUB)
                    utils.drawCloud(surface, camera, x, y, image)
                elif self.weather == "RAIN":
                    brighten = 130
                    image.fill((brighten, brighten, brighten), special_flags=pygame.BLEND_RGB_SUB)
                    utils.drawCloud(surface, camera, x, y, image)
                elif self.weather == "CLOUD":
                    utils.drawCloud(surface, camera, x, y, image)

    def renderLabels(self, surface, camera):
        x = self.loc[0]
        y = self.loc[1]
        if self.visible:
            if self.label != "":
                utils.drawLabel(surface, camera, x, y, self.label, (255, 255, 255))
        elif self.remembered:
            if self.rLabel != "":
                utils.drawLabel(surface, camera, x, y, self.rLabel, (0, 0, 0))

    def get_bounds(self, camera):
        x = self.loc[0]
        y = self.loc[1]
        return utils.getBounds(camera, x, y)

    def add_neighbour(self, neighbour):
        self.neighbours.append(neighbour)
