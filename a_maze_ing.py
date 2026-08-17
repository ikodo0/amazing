import sys
from pydantic import ValidationError
from app.main.screens import MazeScreen, MainMenuScreen, GameMenuScreen
from app.renderer.renderer import Renderer
from app.renderer.screen import ScreenFactory
from app.main.state import SharedState


def main() -> None:
    if len(sys.argv) == 2:
        try:
            state = SharedState()
        except Exception as e:
            print(e, file=sys.stderr)
            sys.exit(1)

        renderer = Renderer(
            height=state.config.WINDOW_HEIGHT,
            width=state.config.WINDOW_WIDTH)

        screen_factory = ScreenFactory()
        screen_factory.register('default', MainMenuScreen(state))
        screen_factory.register('maze', MazeScreen(state))
        screen_factory.register('game_menu', GameMenuScreen(state))

        renderer.screen_factory = screen_factory

        try:
            renderer.show()
        except Exception:
            renderer.close()
    else:
        print("Usage: python3 a_maze_ing.py config.txt", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
