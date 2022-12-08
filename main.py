import os

import numpy as np
import pygame as pg

import assets.objects as objects

from assets.objects import Vec2D
from config import config as cfg
from core import *


if __name__ == '__main__':
    # init pygame
    pg.init()

    # init fonts
    load_fonts(cfg)

    # init game
    screen, clock, fps = init(cfg)

    # load map
    statics = load_map(os.path.join('assets', 'maps', 'test.npy'), cfg=cfg)

    # init static objects
    object_manager = ObjectManager(cfg=cfg)
    object_manager.add(statics)

    # init players
    add_players(object_manager, cfg)

    # init counters
    add_counters(object_manager, cfg)

    # init action manager
    action_manager = ActionManager(object_manager, cfg=cfg)

    # core loop
    while True:
        # events
        for event in pg.event.get():
            # quit the game
            if event.type == pg.QUIT:
                quit()
            if event.type == pg.KEYDOWN:
                # player 1 movement
                for p in range(1, 3): # TODO: change to number of manually controlled players
                    if event.key == getattr(cfg.controls, f'k_p{p}_up'):
                        object_manager.players[p].movement_buffer.x = 0
                        object_manager.players[p].movement_buffer.y = -1
                    if event.key == getattr(cfg.controls, f'k_p{p}_down'):
                        object_manager.players[p].movement_buffer.x = 0
                        object_manager.players[p].movement_buffer.y = 1
                    if event.key == getattr(cfg.controls, f'k_p{p}_left'):
                        object_manager.players[p].movement_buffer.x = -1
                        object_manager.players[p].movement_buffer.y = 0
                    if event.key == getattr(cfg.controls, f'k_p{p}_right'):
                        object_manager.players[p].movement_buffer.x = 1
                        object_manager.players[p].movement_buffer.y = 0
            if event.type == pg.KEYUP:
                # drop bomb
                for p in range(1, 3): # TODO: change to number of manually controlled players
                    if event.key == getattr(cfg.controls, f'k_p{p}_drop_bomb'):
                        if object_manager.players[p].n_bombs > 0:
                            object_manager.players[p].action_buffer.append(actions.DROP_BOMB)
                            object_manager.players[p].n_bombs -= 1

        # handle player movement
        action_manager.handle_player_movement()

        # handle player actions
        action_manager.handle_player_actions()

        # handle collisions
        action_manager.handle_player_collisions()
        action_manager.handle_explosion_collisions()

        # update
        screen.fill(cfg.colors.background_color)

        object_manager.draw_all(screen)
        object_manager.update()

        pg.display.flip()

        # refresh rate
        clock.tick(fps)

    quit()