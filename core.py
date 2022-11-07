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


def load_map(fname, cfg=None):
    """Load map from binary NPY file."""
    mat = np.load(fname)
    objs = []

    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            if mat[i][j] == 1:
                objs.append(objects.SolidWall(Vec2D([i * 32, + j * 32])))
            if mat[i][j] == 2:
                objs.append(objects.BreakableWall(Vec2D([i * 32, + j * 32])))

    return objs


class ObjectManager:
    """Object rendering manager."""
    def __init__(self, cfg=None):
        self.cfg = cfg

        # object rendering lists
        self.render_buffer = []
        self.render_list = OrderedDict()

        # object lifespan lists
        self.lifespan_counts = np.zeros(self.cfg.core.object_limit + 1)
        self.lifespan_limits = np.repeat(np.inf, self.cfg.core.object_limit + 1)

        self.object_counts = 0

        # pointer directly to player object if applicable
        self.player = None


    def __iter__(self):
        return iter(self.render_list.values())


    def add(self, objs):
        """Adds objects to the render list and update lifespans."""
        # set player pointer
        if isinstance(objs, objects.Player):
            self.player = objs

        if not isinstance(objs, list):
            objs = [objs]

        # add objects
        for obj in objs:
            if self.object_counts >= self.cfg.core.object_limit:
                return

            self.render_list[self.object_counts] = obj
            self.lifespan_limits[self.object_counts] = obj.lifespan

            self.object_counts += 1


    def kill(self, idx):
        """Removes object from render list and lifespan lists."""
        # remove and shift elements based on index
        self.lifespan_counts[idx:-1] = self.lifespan_counts[idx + 1:]
        self.lifespan_counts[-1] = 0

        self.lifespan_limits[idx:-1] = self.lifespan_limits[idx + 1:]
        self.lifespan_limits[-1] = np.inf

        self.render_list[idx].on_kill(self)
        del self.render_list[idx]

        self.object_counts -= 1


    def update(self):
        """Update object status, called every frame."""
        # add objects from buffer and clear buffer
        self.add(self.render_buffer)
        self.render_buffer = []

        # update and increment lifespan counts
        lifespans = [obj.lifespan for obj in self.render_list.values()]
        self.object_counts = len(lifespans)
        
        self.lifespan_limits[:self.object_counts] = lifespans
        self.lifespan_counts[:self.object_counts] += 1 / self.cfg.display.refresh_rate

        # if lifespan > lifespan limit, remove object(s)
        to_kill = np.where(self.lifespan_counts > self.lifespan_limits)[0]

        for idx in to_kill:
            self.kill(idx)

        self.lifespan_counts[self.object_counts:] = 0
        self.lifespan_limits[self.object_counts:] = np.inf

        # reset index
        self.render_list = dict(zip(range(self.object_counts), self.render_list.values()))


    def get_objects_sprites(self, *args):
        """Get objects and sprites from render list."""
        objects = [object for object in self.render_list.values() if isinstance(object, args)]
        sprites = [object.sprite for object in objects]
        return objects, sprites


class actions:
    """Action constants."""
    DROP_BOMB = 1


class ActionManager:
    """Object interaction manager."""
    def __init__(self, object_manager, cfg=None):
        self.cfg = cfg
        self.object_manager = object_manager

        self.movement_buffer = Vec2D([0, 0])
        self.action_buffer = []


    def handle_player_movement(self):
        """Defines player movement constraints."""
        object_manager = self.object_manager

        # player object can only move in grid-like pattern
        if all(object_manager.player.position % self.cfg.display.tile_size == 0):
            object_manager.player.vector = self.movement_buffer.copy()

        # move player object
        object_manager.player.position += object_manager.player.vector

        # out of bounds constraints
        max_x = self.cfg.display.screen_width - self.cfg.display.tile_size
        max_y = self.cfg.display.screen_height - self.cfg.display.tile_size

        if object_manager.player.position.x < 0: 
            object_manager.player.position.x = 0
        if object_manager.player.position.x > max_x: 
            object_manager.player.position.x = max_x

        if object_manager.player.position.y < 0: 
            object_manager.player.position.y = 0
        if object_manager.player.position.y > max_y: 
            object_manager.player.position.y = max_y


    def handle_player_actions(self):
        """Performs player actions."""
        object_manager = self.object_manager

        # drop bomb behind player position
        if actions.DROP_BOMB in self.action_buffer:
            position = object_manager.player.position.copy()
            if object_manager.player.vector.y == -1: 
                position.y = self.cfg.display.tile_size * np.ceil(position.y / self.cfg.display.tile_size)
            if object_manager.player.vector.y == 1: 
                position.y = self.cfg.display.tile_size * np.floor(position.y / self.cfg.display.tile_size)
            if object_manager.player.vector.x == -1: 
                position.x = self.cfg.display.tile_size * np.ceil(position.x / self.cfg.display.tile_size)
            if object_manager.player.vector.x == 1: 
                position.x = self.cfg.display.tile_size * np.floor(position.x / self.cfg.display.tile_size)

            object_manager.add(objects.Bomb(position, object_manager.player.n_bomb_radius))
            self.action_buffer.remove(actions.DROP_BOMB)


    def handle_player_collisions(self):
        """Handles coliisions between player and other objects."""
        object_manager = self.object_manager

        # player - wall interactions
        _, sprites = object_manager.get_objects_sprites(objects.SolidWall, objects.BreakableWall)
        idx = object_manager.player.sprite.collidelist(sprites)

        if idx >= 0:
            wall = sprites[idx]
            if object_manager.player.vector.y > 0: 
                object_manager.player.position.y = wall.y - self.cfg.display.tile_size
            if object_manager.player.vector.y < 0: 
                object_manager.player.position.y = wall.y + self.cfg.display.tile_size
            if object_manager.player.vector.x > 0: 
                object_manager.player.position.x = wall.x - self.cfg.display.tile_size
            if object_manager.player.vector.x < 0: 
                object_manager.player.position.x = wall.x + self.cfg.display.tile_size

        # player - item interactions
        items, sprites = object_manager.get_objects_sprites(objects.Item)
        idx = object_manager.player.sprite.collidelist(sprites)

        if idx >= 0:
            items[idx].lifespan = 0

        
    def handle_explosion_collisions(self):
        """Handles collisions between explosions and other objects."""
        object_manager = self.object_manager
        
        # explosion - breakable wall interactions
        walls, sprites = object_manager.get_objects_sprites(objects.SolidWall, objects.BreakableWall)
        explosions, _ = object_manager.get_objects_sprites(objects.Explosion)

        for explosion in explosions:
            idxs = explosion.sprite.collidelistall(sprites)
            for idx in idxs:
                wall = walls[idx]
                if isinstance(wall, objects.BreakableWall):
                    wall.lifespan = 0
