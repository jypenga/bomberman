import numpy as np
import pygame as pg

from dataclasses import dataclass


class colors:
    """Color definitions."""
    SOLID_WALL_COLOR = (0, 0, 127)
    BREAKABLE_WALL_COLOR = (0, 0, 255)
    PLAYER_COLOR = (0, 255, 0)
    EXPLOSION_COLOR = (255, 255, 0)
    BOMB_COLOR = (255, 0, 0)
    ITEM_COLOR = (255, 255, 255)


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


class DefaultObject:
    def __init__(self, position, lifespan, color):
        """Initialize the object at position with lifespan and color."""
        self.sprite = pg.Rect(position.x, position.y, 32, 32)

        self.position = position
        self.lifespan = lifespan

        self.color = color


    def draw(self, screen):
        """Draw the object on the screen."""
        pg.draw.rect(screen, self.color, self.sprite)


    def on_kill(self, object_manager):
        """Called when the object's lifespan expires."""
        return


class SolidWall(DefaultObject):
    def __init__(self, position):
        super().__init__(position, np.inf, colors.SOLID_WALL_COLOR)


class BreakableWall(DefaultObject):
    def __init__(self, position):
        super().__init__(position, np.inf, colors.BREAKABLE_WALL_COLOR)


    def on_kill(self, object_manager):
        if np.random.choice(range(10)) == 0:
            object_manager.render_buffer.append(Item(self.position))


class Player(DefaultObject):
    def __init__(self, position):
        super().__init__(position, np.inf, colors.PLAYER_COLOR)

        self.vector = Vec2D([0, 0])

        self.n_bombs = 99
        self.n_lives = 3
        self.n_bomb_radius = 1


    def draw(self, screen):
        self.sprite.update(self.position, (32, 32))
        pg.draw.rect(screen, self.color, self.sprite)


class Explosion(DefaultObject):
    def __init__(self, position):
        super().__init__(position, .5, colors.EXPLOSION_COLOR)


class Bomb(DefaultObject):
    def __init__(self, position, radius):
        super().__init__(position, 2, colors.BOMB_COLOR)

        self.vector = Vec2D([0, 0])
        self.radius = radius


    def draw(self, screen):
        self.sprite.update(self.position, (32, 32))
        pg.draw.rect(screen, self.color, self.sprite)


    def create_explosion(self, object_manager):
        explosions = [Explosion(self.position)]
        _, sprites = object_manager.get_objects_sprites(SolidWall)

        for vec in [[0, -1], [0, 1], [-1, 0], [1, 0]]:
            for i in range(self.radius + 1):
                explosion = Explosion(self.position + Vec2D(vec) * 32 * i)
                if explosion.sprite.collidelist(sprites) > 0:
                    break
                explosions += [explosion]

        object_manager.render_buffer += explosions


    def on_kill(self, object_manager):
        self.create_explosion(object_manager)


class Item(DefaultObject):
    def __init__(self, position):
        super().__init__(position, np.inf, colors.ITEM_COLOR)


    def on_kill(self, object_manager):
        object_manager.player.n_bomb_radius += 1


