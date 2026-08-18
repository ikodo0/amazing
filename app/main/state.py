import colorsys
from itertools import count
from typing import Generator, Iterator

from app.main.config import read_config
from app.renderer.actions import ToggleNavigationCommand
from app.renderer.font import TTFFont
from app.renderer.texture import Texture
from app.renderer.utils import RGB
from mazegen.maze import Maze, MazeGenerator, solve


class AssetManager:
    def __init__(self) -> None:
        self.fonts = {
            'regular': TTFFont("./assets/fonts/ComicRelief-Regular.ttf", 30),
            'minecraft': TTFFont("./assets/fonts/Minecraft.ttf", 35),
        }
        self.textures = {
            'wall': Texture("./assets/textures/wall.xpm"),
            'burger': Texture("./assets/textures/burger.xpm"),
            'cross': Texture("./assets/textures/cross.xpm"),
            'mario': Texture("./assets/textures/mario.xpm"),
            'coin': Texture("./assets/textures/coin.xpm"),
        }

    def get_font(self, name: str) -> TTFFont:
        return self.fonts[name]

    def get_texture(self, name: str) -> Texture:
        return self.textures[name]


def get_next_color(speed: float = 0.03) -> Generator[RGB, None, None]:
    t = 0.0
    for _ in count():
        hue = (t % 1.0)
        r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
        yield RGB(int(r * 255), int(g * 255), int(b * 255))
        t += speed


class SharedState():
    def __init__(self, config_path: str) -> None:
        self.assets = AssetManager()
        self.config_path = config_path
        self.config = read_config(config_path)

        self.menu_cmd = ToggleNavigationCommand('game_menu')

        self.maze_gen = MazeGenerator(
            self.config.WIDTH, self.config.HEIGHT,
            self.config.SEED, self.config.PERFECT,
            self.config.PATTERN, self.config.MODE)
        self.maze = self.maze_gen.generate()
        self.solution = solve(self.maze, self.config.ENTRY, self.config.EXIT)
        self.maze_steps: Iterator[Maze] | None = None
        self.show_path = False
        self.color = get_next_color()

        self.wall_texture = self.assets.get_texture('wall')


__all__ = [
    'SharedState'
]
