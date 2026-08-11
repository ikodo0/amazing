import sys
from pydantic import ValidationError
from app.main.config import read_config
from mazegen import MazeGenerator, Maze, N, W, S, E


def to_text(maze: Maze) -> str:
    return "\n".join(
        "".join(f"{c.walls:X}" for c in row)
        for row in maze.grid
    ) + "\n"


def main() -> None:
    if len(sys.argv) == 2:
        try:
            config = read_config(sys.argv[1])
            m = MazeGenerator(
                config.WIDTH,
                config.HEIGHT,
                config.SEED,
                config.PERFECT,
                config.PATTERN
            ).generate()
            # m = MazeGenerator(10, 10, seed=42).generate()
            print(sum(1 for row in m.grid for c in row if c.walls != 15))
            with open(config.OUTPUT_FILE, "w") as f:
                f.write(to_text(m))
            # m.carve(1, 1, N)
            # print(maze.cell(1,1).walls, maze.cell(1,0).walls)
            # print(maze.has_wall(1,1,W))
            # print(list(maze.neighbors(0,0)))
            # print(list(maze.neighbors(1,1)))
        except (ValidationError) as e:
            for err in e.errors():
                print(err["msg"], file=sys.stderr)
            sys.exit(1)
        except (OSError, ValueError) as e:
            print(e, file=sys.stderr)
            sys.exit(1)
    else:
        print("Usage: python3 a_maze_ing.py config.txt", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
