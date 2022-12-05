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


class DefaultObject:
    """Default object structure."""
    def __init__(self, position, lifespan, color, text):
        """Initialize the object at position with lifespan and color."""
        self.sprite = pg.Rect(position.x, position.y, 32, 32)

        self.position = position
        self.lifespan = lifespan

        self.color = color
        self.text = text


    def draw(self, screen, object_manager):
        """Draw the object on the screen."""
        # update position if applicable
        if isinstance(self, (Player, Bomb)):
            self.sprite.update(self.position, (32, 32))

        # draw sprite
        pg.draw.rect(screen, self.color, self.sprite)
        
        # center text on object sprite if defined
        if isinstance(self, Item):
            transparent = pg.Rect(self.position.x + 1, self.position.y + 1, 30, 30)
            pg.draw.rect(screen, object_manager.cfg.colors.background_color, transparent)

            if self.text:
                font = object_manager.cfg.fonts.item_font
                text = font.render(self.text, True, object_manager.cfg.colors.item_text_color)
                text_rect = text.get_rect(center=self.sprite.center)

                screen.blit(text, text_rect)


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
        self.n_bomb_radius = 20


class Explosion(DefaultObject):
    """Explosion object."""
    def __init__(self, position, color, text=None):
        super().__init__(position, .5, color, text)


class Bomb(DefaultObject):
    """Bomb object."""
    def __init__(self, position, radius, color, text=None):
        super().__init__(position, 2, color, text)

        self.vector = Vec2D([0, 0])
        self.radius = radius


    def create_explosion(self, object_manager, color):
        """Creates cross-like explosion based on radius."""
        explosions = [Explosion(self.position, color=color)]
        _, sprites = object_manager.get_objects_sprites(SolidWall)

        for vec in [[0, -1], [0, 1], [-1, 0], [1, 0]]:
            for i in range(self.radius + 1):
                explosion = Explosion(self.position + Vec2D(vec) * 32 * i, color=color)
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


    def on_kill(self, object_manager):
        """Increase bomb radius when item is destroyed."""
        
        match self.item_type:
            case 'range':
                object_manager.player.n_bomb_radius += 1
            case 'lives':
                pass
            case 'speed':
                pass


