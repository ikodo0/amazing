import random
from typing import Iterator
from collections import deque
from typing import Any
import sys

N, E, S, W = 1, 2, 4, 8

WORD_DELTA = {N: "North", 2: "South", 4: "East", 8: "West"}
DELTA = {N: (0, -1), S: (0, 1), E: (1, 0), W: (-1, 0)}
OPPOSITE = {N: S, S: N, E: W, W: E}

MOVES = {N: 0, E: 1, S: 2, W: 3}
LETTER = {N: "N", S: "S", E: "E", W: "W"}
STEP = {(0, -1): N, (0, 1): S, (1, 0): E, (-1, 0): W}

PATTERN = [
    " X X XXX",
    " X X   X",
    " XXX XXX",
    "   X X  ",
    "   X XXX"
]

PATTERN_W = len(PATTERN[0])
PATTERN_H = len(PATTERN)
MARGIN = 1
MIN_W = PATTERN_W + 2 * MARGIN
MIN_H = PATTERN_H + 2 * MARGIN


class Cell:
    """Base entity of maze."""
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self.walls = N | S | E | W

    def __eq__(self, other):
        if not isinstance(other, Cell):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return not (self == other)


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

    def __getitem__(self, key: tuple[int, int]):
        x, y = key
        return self.grid[y][x]

    def __eq__(self, other):
        if not isinstance(other, Maze):
            return NotImplemented
        return self.grid == other.grid

    def __ne__(self, other):
        if not isinstance(other, Maze):
            return NotImplemented
        return not (self == other)

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

    def uncarve(self, x: int, y: int, d: int) -> None:
        """Takes coords and direction of Cell."""
        """Uncarves 'd' wall on current cell in opposite on 'd' Cell."""
        dx, dy = DELTA[d]
        nx, ny = x + dx, y + dy
        if not self.in_bounds(nx, ny):
            raise ValueError(f"{WORD_DELTA[d]} from ({x}, {y}) is out bound")
        self.cell(x, y).walls |= d
        self.cell(nx, ny).walls |= OPPOSITE[d]

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
        is_perfect: bool = True,
        has_pattern: bool = True,
        mode: str = "dfs"
                ) -> None:
        self.width = width
        self.height = height
        self.seed = seed
        self.is_perfect = is_perfect
        self.has_pattern = has_pattern
        self.mode = mode

    def knock_walls(self, maze: Maze, random_gen: random.Random,
                    walls_protected: set[tuple[int, int]]) -> None:
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
                        if (x, y) in walls_protected or\
                           (x + dx, y + dy) in walls_protected:
                            continue
                        to_carve.append((x, y, d))
        will_carved = len(to_carve) // 10
        for x, y, d in random_gen.sample(to_carve, will_carved):
            maze.carve(x, y, d)
            if creates_open_area(maze, x, y):
                maze.uncarve(x, y, d)

    def generate(self) -> Maze:
        """Randomly carves a perfect maze using DFS."""
        """Checks unvisited neightbors, randomly selectes where to move."""
        """If no movement possible, come back and continue."""
        """It appends and pops until stack is empty."""
        if self.mode not in ("dfs", "dfs_gt"):
            raise ValueError(f"{self.mode} is not supported.")
        maze = Maze(self.width, self.height)
        random_gen = random.Random(self.seed)
        start = (0, 0)
        visited = {start}
        stack = [start]
        walls_protected: set[tuple[int, int]] = set()
        if self.has_pattern:
            if self.width < MIN_W or self.height < MIN_H:
                print(
                    f"maze must be at least {MIN_W}x"
                    f"{MIN_H} for 42 pattern", file=sys.stderr
                )
            else:
                offset_x = (self.width - PATTERN_W) // 2
                offset_y = (self.height - PATTERN_H) // 2
                for py, line in enumerate(PATTERN):
                    for px, c in enumerate(line):
                        if c == "X":
                            walls_protected.add((px + offset_x, py + offset_y))
                for wall in walls_protected:
                    visited.add(wall)
            # print(len(walls_protected), offset_x, offset_y)
        while stack:
            if self.mode == "dfs":
                x, y = stack[-1]
            if self.mode == "dfs_gt":
                x, y = random_gen.choice(stack)
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
                stack.remove((x, y))
        if not self.is_perfect:
            self.knock_walls(maze, random_gen, walls_protected)
        return maze


def to_text(maze: Maze) -> str:
    return "\n".join(
        "".join(f"{c.walls:X}" for c in row)
        for row in maze.grid
    ) + "\n"


def solve(maze: Maze,
          start: tuple[int, int],
          end: tuple[int, int]) -> list[tuple[int, int]]:
    queue = deque([start])
    visited = {start}
    parent = {}
    if start == end:
        raise ValueError(f"start and end values must differ.")
    while queue:
        x, y = queue.popleft()
        if ((x, y) == end):
            break
        for nx, ny, d in maze.neighbors(x, y):
            if maze.has_wall(x, y, d):
                continue
            if ((nx, ny) in visited):
                continue
            visited.add((nx, ny))
            parent[(nx, ny)] = (x, y)
            queue.append((nx, ny))
    if end not in visited:
        raise ValueError(f"no path from {start} to {end}")
    # print(f"parent: {len(parent)},\n\nvisited:
    # {len(visited)},\n\nqueue: {len(queue)}")
    current = end
    solution = []
    solution = deque()
    solution.appendleft(current)
    while True:
        current = parent[current]
        solution.appendleft(current)
        if current == start:
            break
    return solution


def txt_generate(config: Any, m: Maze,
                 s: list[tuple[int, int]]) -> None:
    sx, sy = config.ENTRY
    ex, ey = config.EXIT
    with open(config.OUTPUT_FILE, "w") as f:
        f.write(f"{to_text(m)}")
        f.write(f"\n{sx},{sy}\n{ex},{ey}")
        letters_arr = []
        for i in range(len(s) - 1):
            dx = s[i + 1][0] - s[i][0]
            dy = s[i + 1][1] - s[i][1]
            letters_arr.append(LETTER[STEP[dx, dy]])
        letters = "".join(letters_arr)
        f.write(f"\n\n{letters}")


def is_open_block(maze: Maze, x: int, y: int) -> bool:
    for dy in range(3):
        for dx in range(2):
            if maze.has_wall(x + dx, y + dy, E):
                return False
    for dy in range(2):
        for dx in range(3):
            if maze.has_wall(x + dx, y + dy, S):
                return False
    return True


def find_open_areas(maze: Maze) -> list[tuple[int, int]]:
    """Return top-left corners of any fully open 3x3 block."""
    bad = []
    for y in range(maze.height - 2):
        for x in range(maze.width - 2):
            if is_open_block(maze, x, y):
                bad.append((x, y))
    return bad


def creates_open_area(maze: Maze, x: int, y: int) -> bool:
    """True if any 3x3 block touching (x, y) is fully open."""
    for by in range(y - 2, y + 2):
        for bx in range(x - 2, x + 2):
            if maze.in_bounds(bx, by) and maze.in_bounds(bx + 2, by + 2):
                if is_open_block(maze, bx, by):
                    return True
    return False

