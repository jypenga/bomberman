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
live = ObjectList(cfg=cfg)

live.add(objects.Player())
live.add_list(statics)

buffer_vector = Vec2D([0, 0])
buffer_drop_bomb = 0

# core loop
while True:
    # debug 
    # for item, value in live.dict_objects.items():
    #     print(item, value)

    # events
    for event in pg.event.get():
        # quit the game
        if event.type == pg.QUIT:
            quit()
        if event.type == pg.KEYDOWN:
            # movement
            if event.key == cfg.controls.k_up:
                buffer_vector.x = 0; buffer_vector.y = -1
            if event.key == cfg.controls.k_down:
                buffer_vector.x = 0; buffer_vector.y = 1
            if event.key == cfg.controls.k_left:
                buffer_vector.x = -1; buffer_vector.y = 0
            if event.key == cfg.controls.k_right:
                buffer_vector.x = 1; buffer_vector.y = 0
        if event.type == pg.KEYUP:
            # drop bomb
            if event.key == cfg.controls.k_drop_bomb:
                if live.player.n_bombs > 0:
                    buffer_drop_bomb = 1
                    live.player.n_bombs -= 1

    # grid-constrained actions
    if all(live.player.position % 32 == 0):
        live.player.vector = buffer_vector.copy()

    if buffer_drop_bomb:
        position = live.player.position.copy()
        if live.player.vector.y == -1: position.y = cfg.display.tile_height * np.ceil(position.y / cfg.display.tile_height)
        if live.player.vector.y == 1: position.y = cfg.display.tile_height * np.floor(position.y / cfg.display.tile_height)
        if live.player.vector.x == -1: position.x = cfg.display.tile_width * np.ceil(position.x / cfg.display.tile_width)
        if live.player.vector.x == 1: position.x = cfg.display.tile_width * np.floor(position.x / cfg.display.tile_width)

        live.add(objects.Bomb(position, live.player.n_bomb_radius))
        buffer_drop_bomb = 0
    
    live.player.position += live.player.vector

    # movement constraints
    max_x = cfg.display.screen_width - cfg.display.tile_width
    max_y = cfg.display.screen_height - cfg.display.tile_height

    if live.player.position.x < 0: live.player.position.x = 0
    if live.player.position.x > max_x: live.player.position.x = max_x

    if live.player.position.y < 0: live.player.position.y = 0
    if live.player.position.y > max_y: live.player.position.y = max_y

    # player collisions
    walls, sprites = live.get_objs_sprites(objects.Wall, objects.BreakableWall)
    idx = live.player.sprite.collidelist(sprites)

    if idx >= 0:
        wall = sprites[idx]
        if live.player.vector.y > 0: live.player.position.y = wall.y - cfg.display.tile_height
        if live.player.vector.y < 0: live.player.position.y = wall.y + cfg.display.tile_height
        if live.player.vector.x > 0: live.player.position.x = wall.x - cfg.display.tile_width
        if live.player.vector.x < 0: live.player.position.x = wall.x + cfg.display.tile_width

    # explosion collision
    explosions, _ = live.get_objs_sprites(objects.Explosion)

    for explosion in explosions:
        idxs = explosion.sprite.collidelistall(sprites)
        for idx in idxs:
            wall = walls[idx]
            if isinstance(wall, objects.BreakableWall):
                wall.n_lifespan = 0

    # item collision
    items, sprites = live.get_objs_sprites(objects.Item)
    idx = live.player.sprite.collidelist(sprites)

    if idx >= 0:
        items[idx].n_lifespan = 0

    # update
    screen.fill(colors.BLACK)

    for object in live:
        object.draw(screen)

    live.update()

    pg.display.flip()

    # refresh rate
    clock.tick(fps)

quit()