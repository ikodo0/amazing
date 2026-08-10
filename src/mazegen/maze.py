import random
from typing import Iterator


N, S, E, W = 1, 2, 4, 8

WORD_DELTA = {N: "North", 2: "South", 4: "East", 8: "West"}
DELTA = {N: (0, -1), S: (0, 1), E: (1, 0), W: (-1, 0)}
OPPOSITE = {N: S, S: N, E: W, W: E}

MOVES = {N: 0, E: 1, S: 2, W: 3}
STEP = {(0, -1): N, (0, 1): S, (1, 0): E, (-1, 0): W}


class Cell:
    """Base entity of maze."""
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self.walls = N | S | E | W


class Maze:
    """Where maze grid lives with all methods."""
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
        """Returns bool if inside bounds of maze"""
        return 0 <= x < self.width and 0 <= y < self.height

    def cell(self, x: int, y: int) -> Cell:
        """Returns a cell"""
        return self.grid[y][x]

    def carve(self, x: int, y: int, d: int) -> None:
        """Takes coords and direction of Cell."""
        """Carves 'd' wall on current cell in opposite on 'd' Cell."""
        dx, dy = DELTA[d]
        nx, ny = x + dx, y + dy
        if not self.in_bounds(nx, ny):
            raise ValueError(f"{WORD_DELTA[d]} from ({x}, {y}) is out bound")
        self.cell(x, y).walls &= ~ d
        self.cell(nx, ny).walls &= ~ OPPOSITE[d]

    def has_wall(self, x: int, y: int, d: int) -> bool:
        """Returns bool if has Cell on direction."""
        return bool(self.cell(x, y).walls & d)

    def neighbors(self, x: int, y: int) -> Iterator[tuple[int, int, int]]:
        """Yields list with all neighbors, coords and delta from current."""
        for d, (dx, dy) in DELTA.items():
            nx, ny = x + dx, y + dy
            if self.in_bounds(nx, ny):
                yield nx, ny, d


class MazeGenerator:
    """Class that is exported for generating and solving maze."""
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

    def knock_walls(self, maze: Maze, random_gen: random.Random) -> None:
        """Collects all maze cells where walls are:"""
        """ up (N) and left (W) and in bound."""
        """Than randomly carves 10%."""
        to_carve = []
        for y in range(maze.height):
            for x in range(maze.width):
                for d in (W, N):
                    dx, dy = DELTA[d]
                    if maze.in_bounds(x + dx, y + dy) and\
                       maze.has_wall(x, y, d):
                        to_carve.append((x, y, d))
        will_carved = len(to_carve) // 10
        for x, y, d in random_gen.sample(to_carve, will_carved):
            maze.carve(x, y, d)

    def generate(self) -> Maze:
        """Randomly carves a perfect maze using DFS."""
        """Checks unvisited neightbors, randomly selectes where to move."""
        """If no movement possible, come back and continue."""
        """It appends and pops until stack is empty."""
        maze = Maze(self.width, self.height)
        random_gen = random.Random(self.seed)
        start = (0, 0)
        visited = {start}
        stack = [start]
        while stack:
            x, y = stack[-1]
            not_visited = []
            neighbors = maze.neighbors(x, y)
            for nx, ny, d in neighbors:
                if (nx, ny) not in visited:
                    not_visited.append((nx, ny, d))
            if not_visited:
                nx, ny, d = random_gen.choice(not_visited)
                maze.carve(x, y, d)
                visited.add((nx, ny))
                stack.append((nx, ny))
            else:
                stack.pop()
        if not self.is_perfect:
            self.knock_walls(maze, random_gen)
        return maze
