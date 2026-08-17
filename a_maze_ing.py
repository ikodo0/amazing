import sys
from pydantic import ValidationError
from app.main.config import read_config
from mazegen import MazeGenerator, solve, txt_generate, find_open_areas
from app.main.screens import MazeScreen, MainMenuScreen, GameMenuScreen
from app.renderer.renderer import Renderer
from app.renderer.screen import ScreenFactory
from app.main.state import SharedState

def main() -> None:
    if len(sys.argv) == 2:
        try:
            state = SharedState()

            renderer = Renderer(
                height=state.config.WINDOW_HEIGHT,
                width=state.config.WINDOW_WIDTH)

            screen_factory = ScreenFactory()
            screen_factory.register('default', MainMenuScreen(state))
            screen_factory.register('maze', MazeScreen(state))
            screen_factory.register('game_menu', GameMenuScreen(state))

            renderer.screen_factory = screen_factory

            renderer.show()
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
