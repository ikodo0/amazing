import random

from app.renderer.actions import NavigationCommand
from app.renderer.component import Button, Text, Tile
from app.renderer.screen import Screen
from app.renderer.utils import RGB, Keycode, Rect
from app.main.state import SharedState


class GameMenuScreen(Screen):
    def __init__(self, state: SharedState):
        super().__init__()

        self.state = state
        assets = state.assets
        config = state.config

        self.background = Tile(
            Rect(
                (config.WINDOW_WIDTH // 2) - ((config.WINDOW_WIDTH // 3) // 2),
                config.WINDOW_HEIGHT // 4,
                config.WINDOW_WIDTH // 3,
                config.WINDOW_HEIGHT // 2
            ),
            RGB(255, 255, 255),
            10
        )

        self.title = Text(
            Rect(
                self.background.rect.x,
                self.background.rect.y + 16,
                self.background.rect.w,
                self.background.rect.h // 8
            ),
            assets.get_font('minecraft'),
            "Menu",
            RGB(0, 0, 0),
            20
        )
        self.title.center()

        exit_btn_rect = Rect(
            self.background.rect.x,
            self.background.rect.y +
            (self.background.rect.h - (self.background.rect.h // 6)),
            self.background.rect.w,
            self.background.rect.h // 6
        )
        self.exit_btn = Button(
            exit_btn_rect,
            Text(exit_btn_rect, assets.get_font('minecraft'),
                 "Exit", RGB(255, 0, 0), z=20),
            RGB(255, 255, 255),
            RGB(0, 0, 0, 64),
            z=20
        )
        self.exit_btn.navigation_command = [
            state.menu_cmd,
            NavigationCommand.clear(),
            NavigationCommand.push('default'),
        ]

        redraw_btn_rect = Rect(
            self.background.rect.x,
            self.background.rect.y +
            (self.title.rect.h) + self.background.rect.h // 6,
            self.background.rect.w,
            self.background.rect.h // 6
        )
        self.redraw_btn = Button(
            redraw_btn_rect,
            Text(redraw_btn_rect, assets.get_font('minecraft'),
                 "Redraw", RGB(0, 0, 0), z=20),
            RGB(255, 255, 255),
            RGB(0, 0, 0, 64),
            z=20
        )
        self.redraw_btn.navigation_command = [
            state.menu_cmd,
            NavigationCommand.clear(),
            NavigationCommand.push('maze')
        ]
        self.redraw_btn.on_click_callback = self.redraw_btn_click

        color_btn_rect = Rect(
            self.background.rect.x,
            self.redraw_btn.rect.y +
            (self.redraw_btn.rect.h),
            self.background.rect.w,
            self.background.rect.h // 6
        )
        self.color_btn = Button(
            color_btn_rect,
            Text(color_btn_rect, assets.get_font('minecraft'),
                 "Color", RGB(0, 0, 0), z=20),
            RGB(255, 255, 255),
            RGB(0, 0, 0, 64),
            z=20
        )
        self.color_btn.on_click_callback = self.color_btn_click
        self.color_btn.navigation_command = [
            state.menu_cmd,
            NavigationCommand.clear(),
            NavigationCommand.push('maze')
        ]

        self.components.extend([
            self.background,
            self.title,
            self.exit_btn,
            self.redraw_btn,
            self.color_btn,
        ])

    def redraw_btn_click(self, keycode: Keycode):
        if keycode != Keycode.LEFT:
            return
        self.state.maze_gen.seed = random.randint(0, 2**32 - 1)
        self.state.maze = self.state.maze_gen.generate()

    def color_btn_click(self, keycode: Keycode):
        if keycode != Keycode.LEFT:
            return
        self.state.wall_texture.set_color_offset(RGB(
            random.randrange(0, 255),
            random.randrange(0, 255),
            random.randrange(0, 255),
        ))
