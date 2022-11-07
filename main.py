from localconfig import config as cfg

import os

import numpy as np
import pygame as pg

import assets.colors as colors
import assets.objects as objects

from assets.objects import Vec2D
from core import *


# load settings
cfg.read(open('settings.cfg'))

# init game
screen, clock, fps = init(cfg)

# load map
statics = load_map(os.path.join('assets', 'maps', 'test.npy'), cfg=cfg)

# init objects
object_manager = ObjectManager(cfg=cfg)
action_manager = ActionManager(object_manager, cfg=cfg)

object_manager.add(objects.Player(Vec2D([32, 32])))
object_manager.add(statics)

# core loop
while True:
    # debug 
    # for item, value in object_manager.dict_objects.items():
    #     print(item, value)

    # events
    for event in pg.event.get():
        # quit the game
        if event.type == pg.QUIT:
            quit()
        if event.type == pg.KEYDOWN:
            # movement
            if event.key == cfg.controls.k_up:
                action_manager.movement_buffer.x = 0; action_manager.movement_buffer.y = -1
            if event.key == cfg.controls.k_down:
                action_manager.movement_buffer.x = 0; action_manager.movement_buffer.y = 1
            if event.key == cfg.controls.k_left:
                action_manager.movement_buffer.x = -1; action_manager.movement_buffer.y = 0
            if event.key == cfg.controls.k_right:
                action_manager.movement_buffer.x = 1; action_manager.movement_buffer.y = 0
        if event.type == pg.KEYUP:
            # drop bomb
            if event.key == cfg.controls.k_drop_bomb:
                if object_manager.player.n_bombs > 0:
                    action_manager.action_buffer.append(actions.DROP_BOMB)
                    object_manager.player.n_bombs -= 1

    # grid-constrained actions
    # if all(object_manager.player.position % 32 == 0):
    #     object_manager.player.vector = buffer_vector.copy()

    # if buffer_drop_bomb:
    #     position = object_manager.player.position.copy()
    #     if object_manager.player.vector.y == -1: position.y = cfg.display.tile_height * np.ceil(position.y / cfg.display.tile_height)
    #     if object_manager.player.vector.y == 1: position.y = cfg.display.tile_height * np.floor(position.y / cfg.display.tile_height)
    #     if object_manager.player.vector.x == -1: position.x = cfg.display.tile_width * np.ceil(position.x / cfg.display.tile_width)
    #     if object_manager.player.vector.x == 1: position.x = cfg.display.tile_width * np.floor(position.x / cfg.display.tile_width)

    #     object_manager.add(objects.Bomb(position, object_manager.player.n_bomb_radius))
    #     buffer_drop_bomb = 0
    
    # object_manager.player.position += object_manager.player.vector

    # # movement constraints
    # max_x = cfg.display.screen_width - cfg.display.tile_width
    # max_y = cfg.display.screen_height - cfg.display.tile_height

    # if object_manager.player.position.x < 0: object_manager.player.position.x = 0
    # if object_manager.player.position.x > max_x: object_manager.player.position.x = max_x

    # if object_manager.player.position.y < 0: object_manager.player.position.y = 0
    # if object_manager.player.position.y > max_y: object_manager.player.position.y = max_y

    # handle player movement
    action_manager.handle_player_movement()

    # handle player actions
    action_manager.handle_player_actions()

    # handle collisions
    action_manager.handle_player_collisions()
    action_manager.handle_explosion_collisions()

    # update
    screen.fill(colors.BLACK)

    for object in object_manager:
        object.draw(screen)

    object_manager.update()

    pg.display.flip()

    # refresh rate
    clock.tick(fps)

quit()