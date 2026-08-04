N, S, E, W = 1, 2, 4, 8
MOVES = {N: 0, E: 1, S: 2, W: 3}
DIRECTION = {(0, -1): N, (0, 1): S, (1, 0): E, (-1, 0): W}


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
    
    def carve(x, y, d) -> None:
        print("ff")
    
    def has_wall(x, y, d) -> None:
        print("ff")


class Cell:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self.walls = N | S | E | W


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
