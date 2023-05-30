import pygame
import utils as utils


class Player:
    loc = 0
    color = None
    name = ""

    def __init__(self, name, location, color):
        self.name = name
        self.loc = location
        self.color = color

    def render(self, surface, camera, tiles, slot = 1):
        tile = ""
        for tile in tiles:
            if tile.id == self.loc:
                break
        x = tile.loc[0]
        y = tile.loc[1]
        if (y % 2) == 0:
            x = x + 0.5
        x = (x * camera["scale"]) + camera["ox"]
        y = (y * camera["scale"] * 0.866) + camera["oy"]
        if not utils.vertical:
            x, y = y, x

        layer = 1
        slot -= layer
        while slot > 0:
            layer += 1
            slot -= layer
        slot += layer

        image = pygame.image.load("..\\MapUIProject\\player_token.png")
        image = pygame.transform.scale(image, (image.get_width() * 0.05, image.get_height() * 0.05))
        image.fill(utils.colors[self.color], special_flags=pygame.BLEND_RGB_MULT)
        brighten = 20
        image.fill((brighten, brighten, brighten), special_flags=pygame.BLEND_RGB_ADD)
        image = pygame.transform.scale(image, (image.get_width() * 3.0, image.get_height() * 3.0))
        spacing = 30
        surface.blit(image, (x - image.get_width() * 0.5 - 3 - ((slot - 1) * spacing) + ((layer - 1) * (spacing / 2)), y - (layer - 1) * (spacing * 0.4)))
