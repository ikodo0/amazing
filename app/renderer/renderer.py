import ctypes
from mlx import Mlx
from app.renderer.actions import NavigationCommand, ScreenAction, \
    ToggleNavigationCommand
from app.renderer.component import DrawCommand, DrawRect, DrawText, \
    DrawTexture
from app.renderer.font import TTFFont
from app.renderer.utils import RGB, Keycode, Rect
from app.renderer.screen import Screen, ScreenFactory
from typing import Any
from time import time
from typing import Callable


class Renderer(Mlx):
    def __init__(
            self,
            height: int = 600,
            width: int = 800,
            title: str = "Application",
            swap_buffers: Callable | None = None,
            screen_factory: ScreenFactory | None = None,
    ) -> None:
        super().__init__()

        self._mlx = self.mlx_init()
        self._win = self.mlx_new_window(self._mlx, width, height, title)

        self.screen_factory = screen_factory

        self._front = self.mlx_new_image(self._mlx, width, height)
        self._front_buffer, _, _, _ = self.mlx_get_data_addr(
            self._front
        )
        self._back = self.mlx_new_image(self._mlx, width, height)
        self._back_buffer, _, self._line_sz, _ = self.mlx_get_data_addr(
            self._back
        )

        self._swap_buffers = swap_buffers

        self._frame = 0
        self._frametime = time()
        self._width = width
        self._height = height

        self._screen_stack: list[Screen] = []

        self._init_time = time()

        self.mlx_hook(self._win, 33, 0, self._hk_close, None)
        self.mlx_mouse_hook(self._win, self._hk_mouse, None)
        self.mlx_loop_hook(self._mlx, self._hk_loop, None)

    @staticmethod
    def _point_in_rect(px: int, py: int, r: Rect) -> bool:
        return (px >= r.x and px <= r.x + r.w and
                py >= r.y and py <= r.y + r.h)

    @property
    def frame(self) -> int:
        return self._frame

    @property
    def height(self) -> int:
        return self._height

    @property
    def width(self) -> int:
        return self._width

    def _hk_mouse(self, code: int, x, y, _param: Any) -> None:
        keycode = Keycode(code)
        for s in self._screen_stack:
            for c in s.components:
                if self._point_in_rect(x, y, c.rect) and \
                   keycode == Keycode.LEFT:
                    c.on_click(keycode)
                    if (hasattr(c, 'navigation_command')):
                        self._handle_navigation(
                            getattr(c, 'navigation_command')
                        )           

    def _handle_navigation(
        self,
        command: list[NavigationCommand | ToggleNavigationCommand]
        | NavigationCommand | ToggleNavigationCommand
    ) -> None:
        if not self.screen_factory:
            return
        if isinstance(command, list):
            for item in command:
                self._handle_navigation(item)
            return
        if isinstance(command, ToggleNavigationCommand):
            cmd = command.execute()
        else:
            cmd = command
        if cmd.action == ScreenAction.PUSH and cmd.screen_name:
            self.push_screen(self.screen_factory.get(cmd.screen_name))
        elif cmd.action == ScreenAction.POP:
            self.pop_screen()
        elif cmd.action == ScreenAction.REPLACE and cmd.screen_name:
            self.pop_screen()
            self.push_screen(self.screen_factory.get(cmd.screen_name))
        elif cmd.action == ScreenAction.CLEAR:
            self.clear_screens()

    def _hk_close(self, _param: Any) -> None:
        self.mlx_destroy_image(self._mlx, self._front)
        self.mlx_destroy_image(self._mlx, self._back)
        self.mlx_destroy_window(self._mlx, self._win)
        self.mlx_loop_exit(self._mlx)

    def _hk_loop(self, _param: Any) -> None:
        if self._mlx is None or self._win is None:
            return

        ctypes.memset(
            ctypes.addressof(self._back_buffer.obj),  # type: ignore
            0, len(self._back_buffer) * 4
        )

        commands: list[DrawCommand] = []

        (_, mouse_x, mouse_y) = self.mlx_mouse_get_pos(self._win)
        for screen in self._screen_stack:
            screen.on_enter()
            for c in screen.components:
                hovered = self._point_in_rect(mouse_x, mouse_y, c.rect)
                commands.extend(c.render(hovered))
            screen.on_exit()

        commands.sort(key=lambda cmd: getattr(cmd, "z", 0))

        self.mlx_clear_window(self._mlx, self._win)

        # commands_start_time = time()
        for cmd in commands:
            if isinstance(cmd, DrawRect):
                self.draw_rect(cmd)
            elif isinstance(cmd, DrawText):
                self.draw_text(cmd)
            elif isinstance(cmd, DrawTexture):
                self.draw_texture(cmd)
        # print(f"All commands executed in: {time() - commands_start_time}")

        if self._swap_buffers:
            self._swap_buffers(self._frame)
        self._front_buffer[:len(self._back_buffer)] = self._back_buffer

        self.mlx_put_image_to_window(
            self._mlx,
            self._win,
            self._front,
            0, 0
        )

        self._frametime = time()

        self.mlx_sync(self._mlx, 1, self._back)
        self.mlx_sync(self._mlx, 2, self._win)
        self.mlx_sync(self._mlx, 3, self._win)

        self._frame += 1

    def show(self) -> None:
        if self.screen_factory:
            self._handle_navigation(
                NavigationCommand(ScreenAction.PUSH, 'default')
            )
        self.mlx_loop(self._mlx)

    def put_pixel(self, x, y, color: RGB):
        if 0 <= x < self._width and 0 <= y < self._height:
            offset = y * self._line_sz + x * 4
            self._back_buffer[offset:offset + 4] = (
                int(color)
            ).to_bytes(4, byteorder='little')

    def put_pixel_blend(self, x: int, y: int, color: RGB, alpha_u8: int):
        if not (0 <= x < self._width and 0 <= y < self._height):
            return

        a_src = max(0, min(255, int(alpha_u8)))

        if a_src == 0:
            return

        offset = y * self._line_sz + x * 4

        dst = int.from_bytes(self._back_buffer[offset:offset + 4],
                             byteorder="little", signed=False)
        dst_a = (dst >> 24) & 0xFF
        dst_r = (dst >> 16) & 0xFF
        dst_g = (dst >> 8) & 0xFF
        dst_b = dst & 0xFF

        src_r = color.r & 0xFF
        src_g = color.g & 0xFF
        src_b = color.b & 0xFF

        src_a = (color.a & 0xFF)
        a = (a_src * src_a) // 255
        if a == 0:
            return

        inv_a = 255 - a

        out_r = (a * src_r + inv_a * dst_r) // 255
        out_g = (a * src_g + inv_a * dst_g) // 255
        out_b = (a * src_b + inv_a * dst_b) // 255

        out_a = (a + (inv_a * dst_a) // 255)

        out = (out_a << 24) | (out_r << 16) | (out_g << 8) | out_b
        self._back_buffer[offset:offset + 4] = out.to_bytes(4,
                                                            byteorder="little")

    def draw_glyph(self, ch: str, x: int, baseline: int, color: RGB,
                   font: TTFFont, z: int = 0):
        g = font.get_glyph(ch)
        if g.w == 0 or g.h == 0:
            return

        x0 = x + g.x_bearing
        y0 = baseline - g.y_bearing

        idx = 0
        for cy in range(g.h):
            for cx in range(g.w):
                a = g.alpha[idx]
                if a:  # skip empty
                    self.put_pixel_blend(x0 + cx, y0 + cy, color, a)
                idx += 1

    def draw_text(self, cmd: DrawText):
        pen_x = cmd.rect.x
        for ch in cmd.text:
            self.draw_glyph(ch, pen_x,
                            cmd.rect.y + cmd.rect.h,
                            cmd.color, cmd.font, cmd.z)
            g = cmd.font.get_glyph(ch)
            pen_x += g.x_advance + cmd.spacing

    def draw_rect(self, cmd: DrawRect) -> None:
        for row in range(cmd.rect.h):
            for col in range(cmd.rect.w):
                self.put_pixel_blend(cmd.rect.x + col, cmd.rect.y + row,
                                     cmd.color, cmd.color.a)

    def draw_texture(self, cmd: DrawTexture):
        texture = cmd.texture
        rect = cmd.rect

        scaled = texture.get_scaled(rect.w, rect.h)

        for y in range(rect.h):
            buffer_offset = (rect.y + y) * self._line_sz + rect.x * 4
            texture_offset = y * rect.w
            # Extract the row as bytes
            row_bytes = b''.join(
                int(color).to_bytes(4, byteorder='little')
                for color in scaled[texture_offset:texture_offset + rect.w]
            )
            # Copy the row in one go
            ctypes.memmove(
                ctypes.addressof(
                    self._back_buffer.obj  # type: ignore
                ) + buffer_offset,
                row_bytes,
                len(row_bytes)
            )

    def push_screen(self, screen: Screen) -> None:
        if screen in self._screen_stack:
            return
        screen.on_mount()
        self._screen_stack.append(screen)

    def pop_screen(self) -> None:
        self._screen_stack.pop()

    def clear_screens(self) -> None:
        self._screen_stack.clear()
