import os

from app.main.config import read_config
from app.renderer.actions import ToggleNavigationCommand
from app.renderer.font import TTFFont
from app.renderer.texture import Texture
from mazegen.maze import MazeGenerator


class AssetManager:
    def __init__(self):
        self.fonts = {
            'regular': TTFFont("./assets/fonts/ComicRelief-Regular.ttf", 30),
            'minecraft': TTFFont("./assets/fonts/Minecraft.ttf", 35),
        }
        self.textures = {
            'wall': Texture("./assets/textures/wall.xpm"),
            'burger': Texture("./assets/textures/burger.xpm"),
            'cross': Texture("./assets/textures/cross.xpm"),
        }

    def get_font(self, name: str) -> TTFFont:
        return self.fonts[name]

    def get_texture(self, name: str) -> Texture:
        return self.textures[name]


class SharedState():
    def __init__(self):
        self.assets = AssetManager()
        self.config = read_config(os.environ.get('CONFIG', 'config.txt'))

        self.menu_cmd = ToggleNavigationCommand('game_menu')

        self.maze_gen = MazeGenerator(
            self.config.WIDTH, self.config.HEIGHT,
            self.config.SEED, self.config.PERFECT,
            self.config.PATTERN or True, self.config.MODE)
        self.maze = self.maze_gen.generate()


__all__ = [
    'SharedState'
]
