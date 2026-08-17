from app.renderer.actions import NavigationCommand
from app.renderer.component import Button, Text, Tile
from app.renderer.screen import Screen
from app.renderer.utils import RGB, Rect
from app.main.state import SharedState


class GameMenuScreen(Screen):
    def __init__(self, state: SharedState):
        super().__init__()

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

        self.components.extend([
            self.background,
            self.title,
            self.exit_btn
        ])
