import math
from time import time

from app.main.config import read_config
from app.renderer.actions import NavigationCommand
from app.renderer.component import Button, Text, Tile
from app.renderer.screen import Screen
from app.renderer.utils import RGB, Keycode, Rect
from app.main.state import SharedState
from mazegen.maze import MazeGenerator


class MainMenuScreen(Screen):
    def __init__(self, state: SharedState):
        super().__init__()

        self.state = state
        assets = state.assets
        config = state.config

        self.title = Text(
            Rect(0, config.WINDOW_HEIGHT // 10, config.WINDOW_WIDTH, 120),
            assets.get_font('minecraft'),
            "A-Maze-ing",
            RGB(255, 255, 255),
            z=100
        )
        self.title.center()

        start_btn_rect = Rect(
            (config.WINDOW_WIDTH // 2) - 90,
            config.WINDOW_HEIGHT // 3, 180, 80
        )
        self.start_btn = Button(
            start_btn_rect,
            Text(start_btn_rect, assets.get_font('regular'),
                 "Start", RGB(255, 255, 255)),
            RGB(255, 200, 1), RGB(0, 255, 0),
        )
        self.start_btn.navigation_command = NavigationCommand.replace('maze')
        # self.start_btn.on_click_callback = self.start_btn_click

        reload_btn_rect = Rect(
            (config.WINDOW_WIDTH // 2) - 90,
            config.WINDOW_HEIGHT // 3 + int(start_btn_rect.h * 1.5),
            180, 80
        )
        self.reload_btn = Button(
            reload_btn_rect,
            Text(reload_btn_rect, assets.get_font('regular'),
                 "Reload", RGB(255, 255, 255)),
            RGB(255, 200, 1), RGB(0, 255, 0)
        )
        self.reload_btn.on_click_callback = self.reload_btn_click

        mario_size = 128
        self.mario_y = config.WINDOW_HEIGHT - mario_size - 32
        self.mario = Tile(
            Rect(0, self.mario_y, mario_size, mario_size),
            assets.get_texture('mario')
        )

        self.components.extend([
            self.title,
            self.start_btn,
            self.reload_btn,
            self.mario
        ])

    # def start_btn_click(self, keycode: Keycode):
    #     if keycode != Keycode.LEFT:
    #         return
    #     self.state.maze_gen.seed = random.randint(0, 2**32 - 1)
    #     self.state.maze = self.state.maze_gen.generate()

    def reload_btn_click(self, keycode: Keycode) -> None:
        if keycode != Keycode.LEFT:
            return
        self.state.config = read_config(self.state.config_path)
        config = self.state.config
        self.state.maze_gen = MazeGenerator(
            config.WIDTH, config.HEIGHT,
            config.SEED, config.PERFECT,
            config.PATTERN, config.MODE)
        self.state.maze = self.state.maze_gen.generate()

    def on_enter(self) -> None:
        """Walk Mario back and forth along the bottom with a hop."""
        span = self.state.config.WINDOW_WIDTH - self.mario.rect.w
        if span <= 0:
            return super().on_enter()
        t = time()
        pos = (t * 120) % (span * 2)
        self.mario.rect.x = int(pos if pos <= span else span * 2 - pos)
        self.mario.rect.y = self.mario_y - int(abs(math.sin(t * 6)) * 40)
        return super().on_enter()

    def on_exit(self) -> None:
        self.title.color = next(self.state.color)
        return super().on_exit()
