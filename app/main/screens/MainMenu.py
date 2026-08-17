import colorsys
from itertools import count
import random

from app.renderer.actions import NavigationCommand
from app.renderer.component import Button, Text
from app.renderer.screen import Screen
from app.renderer.utils import RGB, Keycode, Rect
from app.main.state import SharedState


def get_next_color(speed=0.03):
    t = 0.0
    for _ in count():
        hue = (t % 1.0)
        r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
        yield RGB(int(r * 255), int(g * 255), int(b * 255))
        t += speed


class MainMenuScreen(Screen):
    def __init__(self, state: SharedState):
        super().__init__()

        self.state = state
        assets = state.assets
        config = state.config

        self.color = get_next_color()
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
        self.start_btn.on_click_callback = self.start_btn_click

        self.components.extend([
            self.title,
            self.start_btn
        ])

    def start_btn_click(self, keycode: Keycode):
        if keycode != Keycode.LEFT:
            return
        self.state.maze_gen.seed = random.randint(0, 2**32 - 1)
        self.state.maze = self.state.maze_gen.generate()

    def on_exit(self) -> None:
        self.title.color = next(self.color)
        return super().on_exit()
