from enum import Enum
from typing import Callable


class ScreenAction(Enum):
    """Enum for common screen transitions"""
    PUSH = "push"      # Add screen to stack
    POP = "pop"        # Remove top screen
    REPLACE = "replace"  # Replace top screen
    CLEAR = "clear"    # Clear all screens


class NavigationCommand:
    """Represents a screen navigation action"""
    def __init__(
        self,
        action: ScreenAction,
        screen_name: str = "default"
    ) -> None:
        self.action = action
        self.screen_name = screen_name

    @staticmethod
    def push(screen_name: str) -> 'NavigationCommand':
        return NavigationCommand(ScreenAction.PUSH, screen_name)

    @staticmethod
    def pop() -> 'NavigationCommand':
        return NavigationCommand(ScreenAction.POP)

    @staticmethod
    def replace(screen_name: str) -> 'NavigationCommand':
        return NavigationCommand(ScreenAction.REPLACE, screen_name)

    @staticmethod
    def clear() -> 'NavigationCommand':
        return NavigationCommand(ScreenAction.CLEAR)


class ToggleNavigationCommand:
    def __init__(
        self,
        screen_name: str = "default"
    ) -> None:
        self.screen_name = screen_name
        self.is_open = False
        self.on_state_change: Callable | None = None

    def reset(self) -> None:
        self.is_open = False

    def execute(self) -> NavigationCommand:
        if self.is_open:
            command = NavigationCommand(ScreenAction.POP)
        else:
            command = NavigationCommand(ScreenAction.PUSH, self.screen_name)
        self.is_open = not self.is_open
        if self.on_state_change:
            self.on_state_change(self.is_open)
        return command
