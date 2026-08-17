import colorsys
from itertools import count
import random

from app.renderer import TTFFont, Texture, RGB, Button, Rect, Text, \
      Renderer, Screen, Keycode, Tile, Component, MemoryTexture
from app.renderer.actions import NavigationCommand, ScreenAction, \
    ToggleNavigationCommand
from app.renderer.screen import ScreenFactory
from mazegen import MazeGenerator, N, E, S, W
from mazegen.maze import Maze, solve


class Config:
    class Colors:
        WHITE = RGB(255, 255, 255)
        BLACK = RGB(0, 0, 0)
        RED = RGB(255, 0, 0)
        BUTTON_PRIMARY = RGB(255, 200, 1)
        BUTTON_HOVER = RGB(0, 255, 0)

    class Fonts:
        REGULAR = ("./assets/fonts/ComicRelief-Regular.ttf", 30)
        MINECRAFT = ("./assets/fonts/Minecraft.ttf", 35)

    class Layout:
        TILE_SIZE = 16
        BUTTON_WIDTH = 180
        BUTTON_HEIGHT = 80

    # Window
    WINDOW_WIDTH = 1000
    WINDOW_HEIGHT = 950

    # Asset paths
    TEXTURE_WALL = "./assets/textures/wall.xpm"
    TEXTURE_BURGER = "./assets/textures/burger.xpm"
    TEXTURE_CROSS = "./assets/textures/cross.xpm"

    # Colors
    COLOR_WHITE = RGB(255, 255, 255)
    COLOR_BLACK = RGB(0, 0, 0)
    COLOR_RED = RGB(255, 0, 0)


class AssetManager:
    def __init__(self, config: Config):
        self.fonts = {
            'regular': TTFFont(*config.Fonts.REGULAR),
            'minecraft': TTFFont(*config.Fonts.MINECRAFT),
        }
        self.textures = {
            'wall': Texture(config.TEXTURE_WALL),
            'burger': Texture(config.TEXTURE_BURGER),
            'cross': Texture(config.TEXTURE_CROSS),
        }

    def get_font(self, name: str) -> TTFFont:
        return self.fonts[name]

    def get_texture(self, name: str) -> Texture:
        return self.textures[name]


def create_button(
    rect: Rect,
    text: str,
    font: TTFFont,
    text_color: RGB = RGB(255, 255, 255),
    bg_color: RGB = RGB(255, 200, 1),
    hover_color: RGB = RGB(0, 255, 0),
    z: int = 10
) -> Button:
    """Factory function to reduce boilerplate button creation."""
    return Button(
        rect,
        Text(rect, font, text, text_color, z=z),
        bg_color,
        hover_color,
        z=z
    )


class BurgerButton(Button):
    def __init__(self, rect: Rect, textures: list[Texture]):
        super().__init__(rect, textures[0])
        self.textures = textures
        self.is_open = False

    def set_state(self, state: bool):
        self.is_open = state
        self.texture = self.textures[self.is_open]


def create_button_texture(
    rect: Rect,
    texture: Texture,
    z: int = 10
) -> Button:
    return Button(
        rect,
        texture,
        z=100,
    )


def create_title(
    rect: Rect,
    text: str,
    font: TTFFont,
    color: RGB = RGB(255, 255, 255),
    z=0
) -> Text:
    """Factory for title text elements."""
    title = Text(rect, font, text, color, z=z)
    title.center()
    return title


def get_next_color(speed=0.03):
    t = 0.0
    for _ in count():
        hue = (t % 1.0)
        r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
        yield RGB(int(r * 255), int(g * 255), int(b * 255))
        t += speed


def render_maze(maze: Maze, assets: AssetManager) -> list[Component]:
    maze_width = maze.width * 2 + 3
    # maze_height = maze.height * 2 + 3
    tile_size = 16

    tiles: list[Component] = []
    offset_x = (config.WINDOW_WIDTH // 2) - (maze_width * tile_size) // 2
    offset_y = 64

    for y in range(maze.height):
        for x in range(maze.width):
            cell = maze[(x, y)]

            grid_x = 1 + x * 2
            grid_y = 1 + y * 2

            square = [
                Tile(
                    Rect(
                        offset_x + (grid_x + dx) * tile_size,
                        offset_y + (grid_y + dy) * tile_size,
                        tile_size, tile_size
                    ),
                    assets.get_texture('wall')
                )
                for dy in range(3)
                for dx in range(3)
            ]

            def idx(dx, dy):
                return dy * 3 + dx

            tiles.append(Tile(
                Rect(
                    offset_x + grid_x * tile_size,
                    offset_y + grid_y * tile_size,
                    tile_size, tile_size
                ),
                RGB(255, 0, 0)
            ))
            to_remove = set()
            to_remove.add(idx(1, 1))

            if not (cell.walls & N):
                to_remove.add(idx(1, 0))

            # S edge at (1,2)
            if not (cell.walls & S):
                to_remove.add(idx(1, 2))

            # W edge at (0,1)
            if not (cell.walls & W):
                to_remove.add(idx(0, 1))

            # E edge at (2,1)
            if not (cell.walls & E):
                to_remove.add(idx(2, 1))

            tiles.extend([t for i, t in enumerate(square) if i not in to_remove])

    return tiles


def bake_maze_walls_texture(
    maze: Maze,
    wall_texture: Texture,  # used for sampling per baked tile (optional but you want wall look)
    tile_size: int,
    offset_x: int,
    offset_y: int,  # not needed for pixels, but keep signature consistent
) -> Tile:
    maze_width = maze.width * 2 + 3
    maze_height = maze.height * 2 + 3

    W = maze_width * tile_size
    H = maze_height * tile_size

    # Output pixel buffer as packed 0xAARRGGBB ints
    out_pixels = [0] * (W * H)

    # Helper: write a tile-sized solid/texture-sampled block into out_pixels.
    # We’ll sample from wall_texture so the baked result matches your wall texture styling.
    def blit_wall_tile(dst_x0: int, dst_y0: int):
        # dst_x0/dst_y0 are in baked pixel coordinates (top-left)
        for py in range(tile_size):
            for px in range(tile_size):
                # Sample wall texture proportionally to the tile
                tex_x = (px * wall_texture.width) // tile_size
                tex_y = (py * wall_texture.height) // tile_size
                packed = wall_texture.pixels[tex_y * wall_texture.width + tex_x]
                out_pixels[(dst_y0 + py) * W + (dst_x0 + px)] = packed

    def idx(dx, dy):  # index into 3x3
        return dy * 3 + dx

    for cy in range(maze.height):
        for cx in range(maze.width):
            cell = maze[(cx, cy)]

            grid_x = 1 + cx * 2
            grid_y = 1 + cy * 2

            # Start with "all 9 are walls", then remove as needed.
            removed = set()
            removed.add(idx(1, 1))  # center removed

            if not (cell.walls & N):
                removed.add(idx(1, 0))
            if not (cell.walls & S):
                removed.add(idx(1, 2))
            if (cx > 0) and not (cell.walls & W):
                removed.add(idx(0, 1))
            if (cy < maze.width) and not (cell.walls & E):
                removed.add(idx(2, 1))

            # Optionally ignore corners entirely (comment out if you want corner tiles):
            # removed.update({idx(0,0), idx(2,0), idx(0,2), idx(2,2)})

            for dy in range(3):
                for dx in range(3):
                    if idx(dx, dy) in removed:
                        continue

                    # Convert local 3x3 coords into baked pixel coords
                    px0 = (grid_x + dx) * tile_size
                    py0 = (grid_y + dy) * tile_size
                    blit_wall_tile(px0, py0)

    return Tile(Rect(offset_x, offset_y, W, H), MemoryTexture(W, H, out_pixels))


def render_solution_path(
    maze: Maze,
    start: tuple[int, int],
    end: tuple[int, int],
    solve_fn,
    tile_size: int = 16,
    offset_x: int = 0,
    offset_y: int = 64,
) -> list[Tile]:
    path_cells = solve_fn(maze, start, end)

    line_width = tile_size // 4  # ~4 pixels for tile_size=16

    def cell_center(cx: int, cy: int) -> tuple[int, int]:
        grid_x = 1 + cx * 2
        grid_y = 1 + cy * 2
        # center tile’s top-left pixel
        return (
            offset_x + (grid_x + 1) * tile_size + tile_size // 2,
            offset_y + (grid_y + 1) * tile_size + tile_size // 2,
        )

    tiles: list[Tile] = []

    for i in range(len(path_cells) - 1):
        x1, y1 = cell_center(*path_cells[i])
        x2, y2 = cell_center(*path_cells[i + 1])

        # Vertical movement (same x)
        if x1 == x2:
            connector_rect = Rect(
                x1 - line_width // 2,
                min(y1, y2),
                line_width,
                abs(y2 - y1) + 1
            )
        # Horizontal movement (same y)
        else:
            connector_rect = Rect(
                min(x1, x2),
                y1 - line_width // 2,
                abs(x2 - x1) + 1,
                line_width
            )

        tiles.append(Tile(connector_rect, RGB(255, 0, 0)))

    return tiles


def to_text(maze: Maze) -> str:
    return "\n".join(
        "".join(f"{c.walls:X}" for c in row)
        for row in maze.grid
    ) + "\n"


if __name__ == '__main__':
    maze_gen = MazeGenerator(
        25,
        25,
        mode="dfs_gt"
    )
    maze = maze_gen.generate()

    config = Config()
    assets = AssetManager(config)

    colors = get_next_color()

    background = []

    def swap_buffers(frame: int):
        main_menu.components.append(Tile(
            Rect(
                random.randint(0, config.WINDOW_WIDTH - 16),
                random.randint(0, config.WINDOW_HEIGHT - 16),
                16, 16
            ),
            assets.get_texture('wall'),
            z=-1
        ))
        main_title.color = next(colors)
        pass

    renderer = Renderer(
        swap_buffers=swap_buffers,
        height=config.WINDOW_HEIGHT,
        width=config.WINDOW_WIDTH)

    bg = Tile(
        Rect(
            (config.WINDOW_WIDTH // 2) - ((config.WINDOW_WIDTH // 3) // 2),
            config.WINDOW_HEIGHT // 4,
            config.WINDOW_WIDTH // 3,
            config.WINDOW_HEIGHT // 2
        ),
        RGB(255, 255, 255),
        10
    )
    title = Text(
        Rect(
            bg.rect.x,
            bg.rect.y + 16,
            bg.rect.w,
            bg.rect.h // 8
        ),
        assets.get_font('minecraft'),
        "Menu",
        RGB(0, 0, 0),
        20
    )
    title.center()

    exit_btn = create_button(
        Rect(
                bg.rect.x,
                bg.rect.y + (bg.rect.h - (bg.rect.h // 6)),
                bg.rect.w,
                bg.rect.h // 6
            ),
        "Exit",
        assets.get_font('minecraft'),
        RGB(255, 0, 0),
        RGB(255, 255, 255),
        RGB(0, 0, 0, 64),
        z=20
    )

    def exit_btn_callback(keycode: Keycode):
        if keycode != Keycode.LEFT:
            return
        burger_btn.set_state(False)
        burger_command.reset()

    exit_btn.navigation_command = [
        NavigationCommand(ScreenAction.CLEAR),
        NavigationCommand(ScreenAction.PUSH, 'default')
    ]
    exit_btn.on_click_callback = exit_btn_callback

    rerender_btn = create_button(
        Rect(
            bg.rect.x,
            bg.rect.y + exit_btn.rect.h,
            bg.rect.w,
            bg.rect.h // 6
        ),
        "Refresh",
        assets.get_font('minecraft'),
        RGB(0, 64, 0),
        RGB(255, 255, 255),
        RGB(0, 0, 0, 64),
        z=20
    )

    def maze_render_callback(keycode: Keycode):
        if keycode != Keycode.LEFT:
            return
        game_screen.components.clear()
        maze_gen.seed = random.randint(0, 2**32 - 1)
        current_maze = maze_gen.generate()
        with open("maze.txt", "w") as f:
            f.write(to_text(current_maze))
        burger_btn.set_state(False)
        burger_command.reset()
        game_screen.components.extend([
            bake_maze_walls_texture(current_maze, assets.get_texture('wall'), 16,
                                      offset_x=(config.WINDOW_WIDTH // 2) - ((maze.width * 2 + 3) * 16) // 2, offset_y=64),
            burger_btn,
            *render_solution_path(current_maze, (0, 0), (24, 24), solve_fn=solve, offset_x=(config.WINDOW_WIDTH // 2) - ((maze.width * 2 + 3) * 16) // 2, offset_y=64)
        ])

    rerender_btn.navigation_command = NavigationCommand(ScreenAction.POP)
    rerender_btn.on_click_callback = maze_render_callback

    game_menu_screen = Screen(bg, title, exit_btn, rerender_btn)

    burger_command = ToggleNavigationCommand('game_menu')
    burger_btn = BurgerButton(
        Rect(0, 0, 64, 64),
        [assets.get_texture('burger'), assets.get_texture('cross')],
    )
    burger_command.on_state_change = burger_btn.set_state
    burger_btn.navigation_command = burger_command

    game_screen = Screen(*render_maze(maze, assets), burger_btn)

    main_title = create_title(
        Rect(0, config.WINDOW_HEIGHT // 10, config.WINDOW_WIDTH, 120),
        "A-Maze-ing",
        assets.get_font('minecraft'),
        RGB(255, 255, 255),
        z=999999999
    )

    start_btn = create_button(
        Rect((config.WINDOW_WIDTH // 2) - 90, config.WINDOW_HEIGHT // 3, 180, 80),
        "Start",
        assets.get_font('regular'),
        RGB(255, 255, 255),
        RGB(255, 200, 1), RGB(0, 255, 0),
    )

    start_btn.on_click_callback = maze_render_callback
    start_btn.navigation_command = NavigationCommand.replace('maze')

    settings_btn = create_button(
        Rect((config.WINDOW_WIDTH // 2) - 90, start_btn.rect.y + 100, 180, 80),
        "EINSTELLUNG",
        assets.get_font('regular'),
        RGB(255, 255, 255),
        RGB(255, 200, 1), RGB(0, 255, 0)
    )

    main_menu = Screen(
        main_title,
        start_btn,
        settings_btn,
    )

    screen_factory = ScreenFactory()
    screen_factory.register('default', main_menu)
    screen_factory.register('maze', game_screen)
    screen_factory.register('game_menu', game_menu_screen)

    renderer.screen_factory = screen_factory

    renderer.show()
