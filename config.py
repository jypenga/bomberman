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

        # fonts (font family, font size)
        self.fonts.default_font = ('VeraMono.ttf', 12)
        self.fonts.item_font = ('VeraMono.ttf', 12)
        self.fonts.score_font = ('VeraMono.ttf', 16)

        # display
        self.display.screen_width = 672
        self.display.screen_height = 672 + 32 * 2

        self.display.tile_size = 32

        self.display.refresh_rate = 96

        self.display.n_score_digits = 8

        # core
        self.core.no_players = 2

        # TODO: set counter positions for player 3 and 4
        self.core.player_spawn_positions = [(32, 64),
                                            (32, 64),
                                            (32, 32),
                                            (32, 32)]
        self.core.score_counter_positions = [(0, 16),
                                             (self.display.screen_width - 16 * 5, 16),
                                             (self.display.screen_height - 32, 32),
                                             (32, 32)]
        self.core.live_counter_positions = [(0, 0),
                                            (self.display.screen_width - 8, 0),
                                            (32, 32),
                                            (32, 32)]

        self.core.window_caption = 'Bomberman'
        self.core.object_limit = 2048

        # scores
        self.core.score_per_wall = 10
        self.core.score_per_item = 50

        # colors
        self.colors.background_color = (0, 0, 0)

        self.colors.solid_wall_color = (0, 0, 127)
        self.colors.breakable_wall_color = (0, 0, 255)

        self.colors.player_colors = [(0, 255, 0), (0, 125, 0), (0, 255, 0), (0, 255, 0)]

        self.colors.explosion_color = (255, 255, 0)

        self.colors.bomb_color = (255, 0, 0)

        self.colors.item_color = (255, 255, 255)
        self.colors.item_text_color = (255, 255, 255)

        # controls
        self.controls.k_p1_up = 1073741906
        self.controls.k_p1_down = 1073741905 
        self.controls.k_p1_left = 1073741904
        self.controls.k_p1_right = 1073741903

        self.controls.k_p2_up = 119
        self.controls.k_p2_down = 115
        self.controls.k_p2_left = 97
        self.controls.k_p2_right = 100

        self.controls.k_p1_drop_bomb = 32
        self.controls.k_p2_drop_bomb = 13

        self.controls.k_pause = 27


config = Config()