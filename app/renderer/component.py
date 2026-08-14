from typing import Callable, Protocol
from dataclasses import dataclass
from app.renderer.actions import NavigationCommand, ToggleNavigationCommand
from app.renderer.font import TTFFont
from app.renderer.texture import Texture
from app.renderer.utils import RGB, Keycode, Rect


TextureOrColor = RGB | Texture


class DrawCommand:
    pass


@dataclass
class DrawRect(DrawCommand):
    rect: Rect
    color: RGB
    z: int = 0


@dataclass
class DrawText(DrawCommand):
    text: str
    rect: Rect
    color: RGB
    font: TTFFont
    z: int = 0
    spacing: int = 0


@dataclass
class DrawTexture(DrawCommand):
    rect: Rect
    texture: Texture
    z: int = 0


class Component(Protocol):
    visible: bool
    rect: Rect

    def render(self, hovered: bool) -> list[DrawCommand]:
        ...

    def on_click(self, key: Keycode):
        ...


class RectComponent(Component):
    def __init__(self, rect: Rect, color: RGB, z: int = 0):
        self.rect = rect
        self.color = color
        self.z = z
        self.visible = True

    def render(self, hovered: bool) -> list[DrawCommand]:
        if not self.visible:
            return []
        return [
            DrawRect(self.rect, self.color, self.z)
        ]

    def on_click(self, key: Keycode):
        ...


class Tile(Component):
    def __init__(self, rect: Rect, texture_or_color: TextureOrColor,
                 z: int = 0):
        self.rect = rect
        self.visible = True
        if type(texture_or_color) is RGB:
            self.color = texture_or_color
        elif isinstance(texture_or_color, Texture):
            self.texture = texture_or_color
        else:
            return
        self.z = z

    def render(self, hovered: bool) -> list[DrawCommand]:
        if hasattr(self, 'color'):
            return [DrawRect(self.rect, self.color)]
        return [DrawTexture(self.rect, self.texture)]

    def on_click(self, key: Keycode):
        pass


class Text(Component):
    def __init__(self, rect: Rect, font: TTFFont,
                 text: str, color: RGB, z: int = 0):
        self.rect = rect
        self.text = text
        self.font = font
        self.color = color
        self.visible = True
        self.z = z

    def render(self, hovered: bool, centered=False) -> list[DrawCommand]:
        """Render the text and return draw commands."""
        if not self.visible:
            return []
        return [DrawText(self.text, self.rect,
                         self.color, self.font, z=self.z)]

    def center(self):
        """Calculate and return a rect with text centered within self.rect."""
        text_width, text_height = self.font.measure_text(self.text)
        center_x = self.rect.x + (self.rect.w - text_width) // 2
        center_y = self.rect.y + (self.rect.h - text_height) // 2
        self.rect = Rect(center_x, center_y, text_width, text_height)

    def on_click(self, key: Keycode):
        ...


class Button(Component):
    navigation_command: list[NavigationCommand | ToggleNavigationCommand] |\
          NavigationCommand | ToggleNavigationCommand | None

    def __init__(self, rect: Rect, text_or_texture: Text | Texture,
                 color: RGB | None = None,
                 hover_color: RGB | None = None, z: int = 0):
        self.rect = rect
        if type(text_or_texture) is Text:
            self.text = text_or_texture
            self.text.center()
        elif type(text_or_texture) is Texture:
            self.texture = text_or_texture
        self.color = color
        self.hover_color = hover_color if hover_color else color
        self.visible = True
        self.z = z
        self.on_click_callback: Callable | None = None

    def render(self, hovered: bool) -> list[DrawCommand]:
        """Render the button and return draw commands."""
        if not self.visible:
            return []

        commands: list[DrawCommand] = []

        bg_color = self.hover_color if hovered else self.color

        if bg_color:
            commands.append(DrawRect(self.rect, bg_color, z=self.z))
        if hasattr(self, 'text'):
            commands.extend(self.text.render(hovered))
        elif hasattr(self, 'texture'):
            commands.append(DrawTexture(self.rect, self.texture))

        return commands

    def on_click(self, key: Keycode):
        if self.on_click_callback is not None:
            self.on_click_callback(key)
