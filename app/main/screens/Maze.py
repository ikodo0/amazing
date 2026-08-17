import colorsys
from itertools import count

from app.renderer.component import Button, Tile
from app.renderer.screen import Screen
from app.renderer.texture import MemoryTexture, Texture
from app.renderer.utils import RGB, Rect
from mazegen.maze import N, E, S, W, solve
from app.main.state import SharedState


def get_next_color(speed=0.03):
    t = 0.0
    for _ in count():
        hue = (t % 1.0)
        r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
        yield RGB(int(r * 255), int(g * 255), int(b * 255), 200)
        t += speed


color = get_next_color()


class BurgerButton(Button):
    def __init__(self, rect: Rect, textures: list[Texture]):
        super().__init__(rect, textures[0])
        self.textures = textures
        self.is_open = False

    def set_state(self, state: bool):
        self.is_open = state
        self.texture = self.textures[self.is_open]


class MazeScreen(Screen):
    def __init__(self, state: SharedState):
        super().__init__()

        self.tile_size = 16
        self.assets = state.assets
        self.config = state.config
        self.color = get_next_color()

        self.state = state
        self.maze = self.state.maze

        self.offset_x = (self.config.WINDOW_WIDTH // 2) - \
            ((self.state.maze.width * 2 + 3) * 16) // 2
        self.offset_y = 64

        self.solution = self.solution_path(self.config.ENTRY, self.config.EXIT)

        self.menu_btn = BurgerButton(
            Rect(0, 0, 64, 64),
            [
                self.assets.get_texture('burger'),
                self.assets.get_texture('cross')
            ],
        )
        state.menu_cmd.on_state_change = self.menu_btn.set_state
        self.menu_btn.navigation_command = state.menu_cmd

        self.components.extend([
            self.menu_btn,
            self.bake_maze_walls()
        ])

    def on_mount(self) -> None:
        self.config = self.state.config
        self.maze = self.state.maze
        self.components.clear()
        self.components.extend([
            self.menu_btn,
            self.bake_maze_walls()
        ])
        self.solution = self.solution_path(self.config.ENTRY, self.config.EXIT)

    def on_enter(self) -> None:
        if len(self.solution) > 0:
            tile = self.solution.pop(0)
            self.components.append(tile)
        return super().on_enter()

    def bake_maze_walls(self) -> Tile:
        maze_width = self.state.maze.width * 2 + 3
        maze_height = self.state.maze.height * 2 + 3

        WIDTH = maze_width * self.tile_size
        HEIGHT = maze_height * self.tile_size

        out_pixels = [0] * (WIDTH * HEIGHT)

        wall_texture = self.state.wall_texture

        def blit_wall_tile(x0: int, y0: int):
            # dst_x0/dst_y0 are in baked pixel coordinates (top-left)
            for py in range(self.tile_size):
                for px in range(self.tile_size):
                    # Sample wall texture proportionally to the tile
                    tex_x = (px * wall_texture.width) // self.tile_size
                    tex_y = (py * wall_texture.height) // self.tile_size
                    packed = wall_texture.pixels[
                        tex_y * wall_texture.width + tex_x]
                    out_pixels[(y0 + py) * WIDTH + (x0 + px)] = packed

        def idx(dx, dy):  # index into 3x3
            return dy * 3 + dx

        for cy in range(self.state.maze.height):
            for cx in range(self.state.maze.width):
                cell = self.state.maze[(cx, cy)]

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
                if (cy < self.state.maze.width) and not (cell.walls & E):
                    removed.add(idx(2, 1))

                for dy in range(3):
                    for dx in range(3):
                        if idx(dx, dy) in removed:
                            continue

                        # Convert local 3x3 coords into baked pixel coords
                        px0 = (grid_x + dx) * self.tile_size
                        py0 = (grid_y + dy) * self.tile_size
                        blit_wall_tile(px0, py0)

        return Tile(
            Rect(self.offset_x, self.offset_y, WIDTH, HEIGHT),
            MemoryTexture(WIDTH, HEIGHT, out_pixels)
        )

    def solution_path(
        self,
        start: tuple[int, int], end: tuple[int, int]
    ):
        path_cells = solve(self.state.maze, start, end)

        line_width = self.tile_size // 4

        def cell_center(cx: int, cy: int) -> tuple[int, int]:
            grid_x = 1 + cx * 2
            grid_y = 1 + cy * 2
            # center tile’s top-left pixel
            return (
                self.offset_x + (grid_x + 1) *
                self.tile_size + self.tile_size // 2,
                self.offset_y + (grid_y + 1) *
                self.tile_size + self.tile_size // 2,
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
