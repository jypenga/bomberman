import sys

import numpy as np
import pygame as pg

import assets.objects as objects
from assets.objects import Vec2D

from collections import OrderedDict


def init(cfg):
    """Configures and initializes necessary pygame objects."""
    pg.init()

    # config screen
    width = cfg.display.screen_width
    height = cfg.display.screen_height

    screen = pg.display.set_mode((width, height))
    pg.display.set_caption(cfg.core.window_caption)

    # config clock
    fps = cfg.display.refresh_rate
    clock = pg.time.Clock()

    return screen, clock, fps


def quit():
    """Quits the game."""
    pg.display.quit()
    pg.quit()
    sys.exit()

    return


def load_map(fname, cfg=None):
    """Load map from binary NPY."""
    mat = np.load(fname)
    objs = []

    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            if mat[i][j] == 1:
                objs.append(objects.Wall(Vec2D([i * 32, + j * 32])))
            if mat[i][j] == 2:
                objs.append(objects.BreakableWall(Vec2D([i * 32, + j * 32])))

    return objs


class ObjectList():
    """Live object container."""

    def __init__(self, cfg=None):
        self.cfg = cfg
        self.buffer_add_list = []

        self.dict_objects = OrderedDict()
        self.list_lifespans = np.zeros(self.cfg.core.object_limit + 1)
        self.list_lifespan_limits = np.repeat(np.inf, self.cfg.core.object_limit + 1)

        self.n_objects = 0

        self.player = None


    def __iter__(self):
        return iter(self.dict_objects.values())


    def add(self, obj):
        if isinstance(obj, objects.Player):
            self.player = obj

        if len(self.dict_objects) >= self.cfg.core.object_limit:
            return

        self.dict_objects[self.n_objects] = obj
        self.list_lifespan_limits[self.n_objects] = obj.n_lifespan

        self.n_objects += 1


    def add_list(self, objs):
        for obj in objs:
            self.add(obj)


    def kill(self, idx):
        self.list_lifespans[idx:-1] = self.list_lifespans[idx + 1:]
        self.list_lifespans[-1] = 0

        self.list_lifespan_limits[idx:-1] = self.list_lifespan_limits[idx + 1:]
        self.list_lifespan_limits[-1] = np.inf

        self.dict_objects[idx].on_kill(self)
        
        del self.dict_objects[idx]

        self.n_objects -= 1


    def update(self):
        self.add_list(self.buffer_add_list)
        self.buffer_add_list = []

        lifespans = [obj.n_lifespan for obj in self.dict_objects.values()]
        self.n_objects = len(lifespans)
        
        self.list_lifespan_limits[:self.n_objects] = lifespans

        self.list_lifespans[:self.n_objects] += 1 / self.cfg.display.refresh_rate

        to_kill = np.where(self.list_lifespans > self.list_lifespan_limits)[0]

        for idx in to_kill:
            self.kill(idx)

        self.list_lifespans[self.n_objects:] = 0
        self.list_lifespan_limits[self.n_objects:] = np.inf

        self.dict_objects = dict(zip(range(self.n_objects), self.dict_objects.values()))


    def get_objs_sprites(self, *args):
        objs = [obj for obj in self.dict_objects.values() if isinstance(obj, args)]
        sprites = [obj.sprite for obj in objs]
        return objs, sprites
