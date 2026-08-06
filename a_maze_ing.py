import sys
from pydantic import ValidationError
from app.main.config import read_config
from mazegen import MazeGenerator, N, S, E, W

if __name__ == "__main__":
    if len(sys.argv) == 2:
        try:
            config = read_config(sys.argv[1])
            maze = MazeGenerator(
                config.WIDTH,
                config.HEIGHT,
                config.SEED,
                config.PERFECT
            ).generate()
            maze.carve(1, 1, N)
            print(maze.cell(1,1).walls, maze.cell(1,0).walls)
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
