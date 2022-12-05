class category:
    """Placeholder to enable use of subattributes."""
    pass


class Config:
    """Game configuration."""
    def __init__(self):
        # initialize categories to hold subattributes
        self.core = category()
        self.fonts = category()
        self.colors = category()
        self.display = category()
        self.controls = category()

        # core
        self.core.window_caption = 'Bomberman'
        self.core.object_limit = 1024

        # fonts
        self.fonts.default_font = 'VeraMono.ttf'
        self.fonts.default_font_size = 12

        self.fonts.item_font = 'VeraMono.ttf'
        self.fonts.item_font_size = 12

        # colors
        self.colors.background_color = (0, 0, 0)

        self.colors.solid_wall_color = (0, 0, 127)
        self.colors.breakable_wall_color = (0, 0, 255)

        self.colors.player_color = (0, 255, 0)

        self.colors.explosion_color = (255, 255, 0)

        self.colors.bomb_color = (255, 0, 0)

        self.colors.item_color = (255, 255, 255)
        self.colors.item_text_color = (255, 255, 255)

        # display
        self.display.screen_width = 672
        self.display.screen_height = 672

        self.display.tile_size = 32

        self.display.refresh_rate = 96

        # controls
        self.controls.k_up = 1073741906
        self.controls.k_down = 1073741905
        self.controls.k_left = 1073741904
        self.controls.k_right = 1073741903

        self.controls.k_drop_bomb = 32

        self.controls.k_pause = 27


config = Config()