import os
import sys

import numpy as np
import pygame as pg

import assets.objects as objects

from assets.objects import Vec2D
from collections import OrderedDict


def init(cfg):
    """Configures and initializes necessary pygame objects."""
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


def load_font(fname, size):
    """Load font from file."""
    return pg.font.Font(os.path.join('assets', 'fonts', fname), size)


def load_fonts(cfg):
    """Load fonts from config."""
    for key, value in cfg.fonts.__dict__.items():
        font_family, font_size = value
        setattr(cfg.fonts, key, load_font(font_family, font_size))


def load_map(fname, cfg=None):
    """Load map from binary NPY file."""
    grid = np.load(fname)
    objs = []

    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            location = Vec2D([i * cfg.display.tile_size, + j * cfg.display.tile_size + 32])
            if grid[i][j] == 1:
                objs.append(objects.SolidWall(location, color=cfg.colors.solid_wall_color))
            if grid[i][j] == 2:
                objs.append(objects.BreakableWall(location, color=cfg.colors.breakable_wall_color))

    return objs


def add_players(object_manager, cfg):
    """Add players to object manager."""
    for i in range(cfg.core.no_players):
        object_manager.add(objects.Player(Vec2D(cfg.core.player_spawn_positions[i]),
                                          color=cfg.colors.player_colors[i]))


def add_counters(object_manager, cfg):
    """Add counters to object manager."""
    for i in range(cfg.core.no_players):
        player = getattr(object_manager.players, f'player_{i + 1}')
        object_manager.add(objects.LiveCounter(Vec2D(cfg.core.live_counter_positions[i]),
                           player=player,
                           color=cfg.colors.player_colors[i]))
        object_manager.add(objects.ScoreCounter(Vec2D(cfg.core.score_counter_positions[i]),
                           player=player,
                           color=cfg.colors.player_colors[i]))


class PlayerContainer:
    """Container for player pointers."""
    def __init__(self, cfg):
        """Initialize player pointers."""
        for i in range(1, cfg.core.no_players + 1):
            setattr(self, 'player_' + str(i), None)


    def __iter__(self):
        """Iterate over players."""
        return iter(player for player in self.__dict__.values() if player)

    
    def __getitem__(self, key):
        """Get player by index, index starts at 1."""
        return getattr(self, 'player_' + str(key))


class ObjectManager:
    """Object rendering manager."""
    def __init__(self, cfg=None):
        self.cfg = cfg

        # object rendering lists
        self.render_buffer = list()
        self.render_list = OrderedDict()

        # object lifespan lists
        self.lifespan_counts = np.zeros(self.cfg.core.object_limit + 1)
        self.lifespan_limits = np.repeat(np.inf, self.cfg.core.object_limit + 1)

        self.object_counts = 0

        # player pointers
        self.players = PlayerContainer(cfg)


    def add(self, objs):
        """Adds objects to the render list and update lifespans."""
        # set player pointers
        if isinstance(objs, objects.Player):
            # set pointers to default players
            if not self.players.player_1:
                self.players.player_1 = objs
            elif not self.players.player_2:
                self.players.player_2 = objs

            # set pointers to optional additional players
            if hasattr(self.players, 'player_3') and not self.player_3:
                self.players.player_3 = objs
            elif hasattr(self.players, 'player_4') and not self.player_4:
                self.players.player_4 = objs

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
        self.render_list.pop(idx)

        self.object_counts -= 1

    
    def draw_all(self, screen):
        """Draw all objects to screen."""
        # draw all objects as ordered in the render list
        for obj in self.render_list.values():
            obj.draw(screen, self)


    def update(self):
        """Update object status, called every frame."""
        # add objects from buffer and clear buffer
        self.add(self.render_buffer)
        self.render_buffer.clear()

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


    def handle_player_movement(self):
        """Defines player movement constraints."""
        # refresh
        object_manager = self.object_manager

        # out of bounds constraints
        max_x = self.cfg.display.screen_width - self.cfg.display.tile_size
        max_y = self.cfg.display.screen_height - self.cfg.display.tile_size

        for player in object_manager.players:   
            # player object can only move in grid-like pattern
            if all(player.position % self.cfg.display.tile_size == 0):
                player.vector = player.movement_buffer.copy()

            # move player object
            player.position += player.vector

            if player.position.x < 0: 
                player.position.x = 0
            if player.position.x > max_x: 
                player.position.x = max_x

            if player.position.y < 0: 
                player.player.position.y = 0
            if player.position.y > max_y: 
                player.player.position.y = max_y


    def handle_player_actions(self):
        """Performs player actions."""
        # refresh
        object_manager = self.object_manager

        # drop bomb behind player position
        for player in object_manager.players:
            if actions.DROP_BOMB in player.action_buffer:
                # drop bomb behind player
                position = player.position.copy()
                if player.vector.y == -1: 
                    position.y = self.cfg.display.tile_size * np.ceil(position.y / self.cfg.display.tile_size)
                if player.vector.y == 1: 
                    position.y = self.cfg.display.tile_size * np.floor(position.y / self.cfg.display.tile_size)
                if player.vector.x == -1: 
                    position.x = self.cfg.display.tile_size * np.ceil(position.x / self.cfg.display.tile_size)
                if player.vector.x == 1: 
                    position.x = self.cfg.display.tile_size * np.floor(position.x / self.cfg.display.tile_size)

                # drop bomb
                object_manager.add(objects.Bomb(position,
                                                player=player,
                                                color=self.cfg.colors.bomb_color))
                player.action_buffer.remove(actions.DROP_BOMB)


    def handle_player_collisions(self):
        """Handles coliisions between player and other objects."""
        # refresh
        object_manager = self.object_manager

        # player - wall interactions
        _, sprites = object_manager.get_objects_sprites(objects.SolidWall, objects.BreakableWall)

        for player in object_manager.players:
            idx = player.sprite.collidelist(sprites)

            if idx >= 0:
                wall = sprites[idx]
                if player.vector.y > 0: 
                    player.position.y = wall.y - self.cfg.display.tile_size
                if player.vector.y < 0: 
                    player.position.y = wall.y + self.cfg.display.tile_size
                if player.vector.x > 0: 
                    player.position.x = wall.x - self.cfg.display.tile_size
                if player.vector.x < 0: 
                    player.position.x = wall.x + self.cfg.display.tile_size

        # player - item interactions
        items, sprites = object_manager.get_objects_sprites(objects.Item)

        for player in object_manager.players:
            idx = player.sprite.collidelist(sprites)

            if idx >= 0:
                items[idx].lifespan = 0

        
    def handle_explosion_collisions(self):
        """Handles collisions between explosions and other objects."""
        # refresh
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
                    explosion.player.n_score += 5
