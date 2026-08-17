from app.main.screens import MazeScreen, MainMenuScreen, GameMenuScreen
from app.renderer.renderer import Renderer
from app.renderer.screen import ScreenFactory
from app.main.state import SharedState


if __name__ == '__main__':
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
