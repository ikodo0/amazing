from enum import Enum


class RGB:
    def __init__(self, r: int, g: int, b: int, a: int = 255):
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    def __int__(self):
        return (self.r << 24) | (self.g << 16) | (self.b << 8) | self.a

    def to_int(self):
        return (self.a << 24) | (self.r << 16) | (self.g << 8) | self.b


class Rect:
    def __init__(self, x: int, y: int, w: int, h: int):
        self.x = x
        self.y = y
        self.w = w
        self.h = h


class Keycode(Enum):
    LEFT = 1
    MIDDLE = 2
    RIGHT = 3
    SCROLL_UP = 4
    SCROLL_DOWN = 5
