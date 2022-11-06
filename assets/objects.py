from turtle import left, up
import numpy as np
import pygame as pg


class Vec2D(np.ndarray):
    """Vector wrapper of numpy ndarray."""

    def __new__(cls, input_array, x=0, y=0):
        obj = np.asarray(input_array, dtype=np.int16).view(cls)

        obj.x = obj[0]
        obj.y = obj[1]

        return obj


    def __array_finalize__(self, obj):
        if obj is None: 
            return

        self.x = getattr(obj, 'x', obj[0])
        self.y = getattr(obj, 'y', obj[1])


    def __getattr__(self, name):
        if name == 'x':
            return self[0]
        elif name == 'y':
            return self[1]
        else:
            return super().__getattr__(name)


    def __setattr__(self, name, value):
        if name == 'x':
            self[0] = value
        elif name == 'y':
            self[1] = value
        else:
            super().__setattr__(name, value)


class Wall(object):
    """Wall object."""

    def __init__(self, position):
        self.position = position

        self.color = (0, 0, 127)
        self.sprite = pg.Rect(self.position.x, self.position.y, 32, 32)

        self.n_lifespan = np.inf

    def draw(self, screen):
        pg.draw.rect(screen, self.color, self.sprite)

    def on_kill(self, obj_list):
        return


class BreakableWall(object):
    """BreakbleWall object."""

    def __init__(self, position):
        self.position = position

        self.color = (0, 0, 255)
        self.sprite = pg.Rect(self.position.x, self.position.y, 32, 32)

        self.n_lifespan = np.inf


    def draw(self, screen):
        # self.sprite.update(self.position, (32, 32))
        pg.draw.rect(screen, self.color, self.sprite)

    def on_kill(self, obj_list):
        if np.random.choice(range(10)) == 0:
            obj_list.buffer_add_list.append(Item(self.position))
        return


class Player(object):
    """Player object."""

    def __init__(self):
        self.position = Vec2D([32, 32])
        self.vector = Vec2D([0, 0])

        self.color = (0, 255, 0)
        self.sprite = pg.Rect(self.position.x, self.position.y, 32, 32)

        self.n_bombs = 99
        self.n_lives = 3
        self.n_lifespan = np.inf

        self.n_bomb_radius = 1

    def draw(self, screen):
        self.sprite.update(self.position, (32, 32))
        pg.draw.rect(screen, self.color, self.sprite)


class Explosion(object):
    """Explosion object."""

    def __init__(self, position):
        self.position = position

        self.color = (255, 255, 0)

        self.sprite = pg.Rect(self.position.x, self.position.y, 32, 32)

        self.n_lifespan = .5

    def draw(self, screen):
        pg.draw.rect(screen, self.color, self.sprite)

    def on_kill(self, obj_list):
        return


def create_explosion(position, obj_list, radius=1):
    explosions = [Explosion(position)]
    _, sprites = obj_list.get_objs_sprites(Wall)

    for vec in [[0, -1], [0, 1], [-1, 0], [1, 0]]:
        for i in range(radius + 1):
            explosion = Explosion(position + Vec2D(vec) * 32 * i)
            if explosion.sprite.collidelist(sprites) > 0:
                break
            explosions += [explosion]

    obj_list.buffer_add_list += explosions
    return


class Bomb(object):
    """Bomb object."""

    def __init__(self, position, radius):
        self.position = position
        self.vector = Vec2D([0, 0])
        self.radius = radius

        self.color = (255, 0, 0)
        self.sprite = pg.Rect(self.position.x, self.position.y, 32, 32)

        self.n_lifespan = 2

    def draw(self, screen):
        # self.sprite.update(self.position, (32, 32))
        pg.draw.rect(screen, self.color, self.sprite)

    def on_kill(self, obj_list):
        create_explosion(self.position, obj_list, self.radius)
        return


class Item(object):
    """Item object."""

    def __init__(self, position):
        self.position = position
        self.vector = Vec2D([0, 0])

        self.color = (255, 255, 255)
        self.sprite = pg.Rect(self.position.x, self.position.y, 32, 32)

        self.n_lifespan = np.inf

    def draw(self, screen):
        # self.sprite.update(self.position, (32, 32))
        pg.draw.rect(screen, self.color, self.sprite)

    def on_kill(self, obj_list):
        obj_list.player.n_bomb_radius += 1
        return

