from __future__ import annotations
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.renderer.screen import Screen


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
        screen: Screen | None = None
    ) -> None:
        self.action = action
        self.screen = screen

    @staticmethod
    def push(screen: Screen) -> 'NavigationCommand':
        return NavigationCommand(ScreenAction.PUSH, screen)

    @staticmethod
    def pop() -> 'NavigationCommand':
        return NavigationCommand(ScreenAction.POP)

    @staticmethod
    def replace(screen: Screen) -> 'NavigationCommand':
        return NavigationCommand(ScreenAction.REPLACE, screen)

    @staticmethod
    def clear() -> 'NavigationCommand':
        return NavigationCommand(ScreenAction.CLEAR)
