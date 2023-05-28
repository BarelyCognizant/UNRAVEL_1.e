import pygame

colors = {"desert": [(201, 173, 71), (232, 212, 139)],
          "forest": [(83, 171, 79), (120, 207, 116)],
          "mesa": [(148, 62, 44), (191, 98, 78)],
          "background": (53, 54, 58)}

tiles = ["forest", "desert", "mesa"]


def getHexagon(x, y, w):
    points = [
        (x + (+0.000 * w * 0.5), y + (+1.000 * w * 0.5)),
        (x + (+0.866 * w * 0.5), y + (+0.500 * w * 0.5)),
        (x + (+0.866 * w * 0.5), y + (-0.500 * w * 0.5)),
        (x + (+0.000 * w * 0.5), y + (-1.000 * w * 0.5)),
        (x + (-0.866 * w * 0.5), y + (-0.500 * w * 0.5)),
        (x + (-0.866 * w * 0.5), y + (+0.500 * w * 0.5))
    ]
    return points


def drawCell(surface, camera, x, y, color):
    if (y % 2) == 0:
        x = x + 0.5
    x = (x * camera["scale"]) + camera["ox"]
    y = (y * camera["scale"] * 0.866) + camera["oy"]
    rect = pygame.draw.polygon(surface, color, getHexagon(x, y, camera["scale"]))
    return rect


def screenToCameraTransform(p, camera):
    x = p[0]
    y = p[1]
    if (y % 2) == 0:
        x = x + 0.5
    x = (x * camera["scale"]) + camera["ox"]
    y = (y * camera["scale"] * 0.866) + camera["oy"]
    return x, y


def addAlphaRect(surface, x, y, w, h, color, a):
    s = pygame.Surface((w, h))
    s.set_alpha(a)
    s.fill(color)
    surface.blit(s, (x, y))


def addText(surface, text, x, y, font, color):
    label = font.render(text, 1, color)
    surface.blit(label, (x, y))


def generate_neighbour_locs(loc):
    x = loc[0]
    y = loc[1]
    ys = [y + 1, y + 1, y, y, y - 1, y - 1]
    if y % 2 == 0:
        return [(x, y-1), (x+1, y-1), (x-1, y), (x+1, y), (x, y+1), (x+1, y+1)]
    else:
        return [(x-1, y - 1), (x, y - 1), (x - 1, y), (x + 1, y), (x-1, y + 1), (x, y + 1)]


def find_tiles(locs, bs):
    ret = []
    for b in bs:
        if b.loc in locs:
            ret.append(b)
    return ret
