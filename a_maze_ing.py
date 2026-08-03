from app.main.config import read_config
from pydantic import ValidationError
import sys

if __name__ == "__main__":
    if len(sys.argv) == 2:
        try:
            config = read_config(sys.argv[1])
            print(config)
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
