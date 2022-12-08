import numpy as np
import pygame as pg

from config import config as cfg


class Vec2D(np.ndarray):
    """Vector wrapper of numpy ndarray."""
    def __new__(cls, input_array, x=0, y=0):
        obj = np.asarray(input_array, dtype=np.int16).view(cls)

        obj.x = obj[0]
        obj.y = obj[1]

        return obj


    def __array_finalize__(self, obj):
        """Finalize x and y attributes."""
        if obj is None: 
            return

        self.x = getattr(obj, 'x', obj[0])
        self.y = getattr(obj, 'y', obj[1])


    def __getattr__(self, name):
        """Get first or second element when requesting x or y attribute."""
        if name == 'x':
            return self[0]
        elif name == 'y':
            return self[1]
        else:
            return super().__getattr__(name)


    def __setattr__(self, name, value):
        """Set x and y attributes to first and second element."""
        if name == 'x':
            self[0] = value
        elif name == 'y':
            self[1] = value
        else:
            super().__setattr__(name, value)


class DefaultObject:
    """Default object structure."""
    def __init__(self, position, lifespan, color, text):
        """Initialize the object at position with lifespan and color."""
        self.sprite = pg.Rect(position.x, position.y, cfg.display.tile_size, cfg.display.tile_size)

        self.position = position
        self.lifespan = lifespan

        self.color = color
        self.text = text


    def draw(self, screen, object_manager):
        """Draw the object on the screen."""
        pg.draw.rect(screen, self.color, self.sprite)


    def on_kill(self, object_manager):
        """Called when the object's lifespan expires."""
        return


class SolidWall(DefaultObject):
    """Unbreakable wall object."""
    def __init__(self, position, color, text=None):
        super().__init__(position, np.inf, color, text)


class BreakableWall(DefaultObject):
    """Breakable wall object."""
    def __init__(self, position, color, text=None):
        super().__init__(position, np.inf, color, text)


    def on_kill(self, object_manager):
        """Spawns item when wall is destroyed."""
        if np.random.choice(range(10)) == 0:
            item_type = None
            item_color = object_manager.cfg.colors.item_color

            match np.random.choice(range(3)):
                case 0:
                    item_type = 'range'
                case 1:
                    item_type = 'lives'
                case 2:
                    item_type = 'speed'

            object_manager.render_buffer.append(Item(self.position, item_type, item_color))


class Player(DefaultObject):
    """Player object."""
    def __init__(self, position, color, text=None):
        super().__init__(position, np.inf, color, text)

        self.vector = Vec2D([0, 0])

        # player attributes
        self.n_bombs = 99
        self.n_lives = 3
        self.n_score = 0
        self.n_bomb_radius = 20

        # movement buffer
        self.movement_buffer = Vec2D([0, 0])
        self.action_buffer = []


    def draw(self, screen, object_manager):
        """Player is a dynamic object; update position and then draw."""
        self.sprite.update(self.position, (self.sprite.width, self.sprite.height))
        super().draw(screen, object_manager)


class Explosion(DefaultObject):
    """Explosion object."""
    def __init__(self, position, player, color, text=None):
        super().__init__(position, .5, color, text)

        # player whose bomb created the explosion
        self.player = player


class Bomb(DefaultObject):
    """Bomb object."""
    def __init__(self, position, player, color, text=None):
        super().__init__(position, 2, color, text)

        # attributes
        self.vector = Vec2D([0, 0])
        self.radius = player.n_bomb_radius

        # player that placed the bomb
        self.player = player


    def draw(self, screen, object_manager):
        """Bomb is a dynamic object; update position and then draw."""
        self.sprite.update(self.position, (self.sprite.width, self.sprite.height))
        super().draw(screen, object_manager)


    def create_explosion(self, object_manager, color):
        """Creates cross-like explosion based on radius."""
        explosions = [Explosion(self.position,
                                player=self.player,
                                color=color)]
        _, sprites = object_manager.get_objects_sprites(SolidWall)

        for vec in [[0, -1], [0, 1], [-1, 0], [1, 0]]:
            for i in range(self.radius + 1):
                explosion = Explosion(self.position + Vec2D(vec) * cfg.display.tile_size * i,
                                      player=self.player,
                                      color=color)
                if explosion.sprite.collidelist(sprites) > 0:
                    break
                explosions += [explosion]

        object_manager.render_buffer += explosions


    def on_kill(self, object_manager):
        """Creates explosion when bomb is destroyed."""
        self.create_explosion(object_manager, color=object_manager.cfg.colors.explosion_color)


class Item(DefaultObject):
    """Item object."""
    def __init__(self, position, item_type, color):
        self.item_type = item_type

        match self.item_type:
            case 'range':
                text = '+1'
            case 'lives':
                text = '<3'
            case 'speed':
                text = '>>'
            case _:
                text = None

        super().__init__(position, np.inf, color, text)


    def draw(self, screen, object_manager):
        """Draw the inner text and border for an item object."""
        super().draw(screen, object_manager)

        transparent = pg.Rect(self.position.x + 1, self.position.y + 1, self.sprite.width - 2, self.sprite.height - 2)
        pg.draw.rect(screen, object_manager.cfg.colors.background_color, transparent)

        if self.text:
            font = object_manager.cfg.fonts.item_font
            text = font.render(self.text, True, self.color)
            text_rect = text.get_rect(center=self.sprite.center)

            screen.blit(text, text_rect)


    def on_kill(self, object_manager):
        """Increase bomb radius when item is destroyed."""
        match self.item_type:
            case 'range':
                object_manager.player.n_bomb_radius += 1
            case 'lives':
                pass
            case 'speed':
                pass


class DefaultCounter(DefaultObject):
    """Default counter object."""
    def __init__(self, position, color, text):
        super().__init__(position, np.inf, color, text)


    def draw(self, screen, object_manager):
        sprite = pg.Rect(self.position.x, self.position.y, *object_manager.cfg.fonts.score_font.size(self.text))

        font = object_manager.cfg.fonts.score_font
        text = font.render(self.text, True, self.color)
        text_rect = text.get_rect(center=sprite.center)

        screen.blit(text, text_rect)


class ScoreCounter(DefaultCounter):
    """Score counter object."""
    def __init__(self, position, player, color, text='0' * cfg.display.n_score_digits):
        super().__init__(position, color, text)
        self.player = player

    def draw(self, screen, object_manager):
        self.text = str(self.player.n_score).zfill(cfg.display.n_score_digits)
        super().draw(screen, object_manager)


class LiveCounter(DefaultCounter):
    """Live counter object."""
    def __init__(self, position, player, color, text='0'):
        super().__init__(position, color, text)
        self.player = player

    def draw(self, screen, object_manager):
        self.text = str(self.player.n_lives).zfill(1)
        super().draw(screen, object_manager)