import random

N, S, E, W = 1, 2, 4, 8

DELTA = {N: (0, -1), S: (0, 1), E: (1, 0), W: (-1, 0)}
OPPOSITE = {N: S, S: N, E: W, W: E}

MOVES = {N: 0, E: 1, S: 2, W: 3}
STEP = {(0, -1): N, (0, 1): S, (1, 0): E, (-1, 0): W}

class Cell:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self.walls = N | S | E | W


class Maze:
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.grid: list[list[Cell]] = []
        for y in range(height):
            row = []
            for x in range(width):
                row.append(Cell(x, y))
            self.grid.append(row)
    

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def cell(self, x: int, y: int) -> Cell:
        return self.grid[y][x]

    def carve(self, x:int , y:int , d: int) -> None:
        dx, dy = DELTA[d]
        nx, ny = x + dx, y + dy
        if not self.in_bounds(nx, ny):
            raise ValueError(f"{d} from ({x}, {y})is out bound")
        self.cell(x, y).walls &= ~d
        self.cell(nx, ny).walls &= ~ OPPOSITE[d]

    def has_wall(self, x: int, y: int, d: int) -> None:
        print("ff")


class MazeGenerator:
    def __init__(
        self,
        width: int,
        height: int,
        seed: int | None = None,
        is_perfect: bool = True
                ) -> None:
        self.width = width
        self.height = height
        self.seed = seed
        self.is_perfect = is_perfect

    def generate(self) -> Maze:
        maze = Maze(self.width, self.height)
        print(maze)
        if not self.is_perfect:
            print("We will carve it")
        return maze
