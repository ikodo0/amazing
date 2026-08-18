import freetype
from dataclasses import dataclass


@dataclass
class Glyph:
    """Represents a rendered glyph."""
    w: int
    h: int
    x_bearing: int
    y_bearing: int
    x_advance: int
    y_advance: int
    alpha: list[int]  # row-major array of alpha values


class TTFFont:
    """TrueType font management using freetype library."""

    def __init__(self, font_path: str, size: int = 12):
        """
        Initialize a TTF font.

        Args:
            font_path: Path to the .ttf or .otf font file
            size: Font size in pixels
        """
        self.face = freetype.Face(font_path)
        self.size = size
        self.set_size(size)
        self._glyph_cache: dict[str, Glyph] = {}

    def set_size(self, size: int) -> None:
        """Set the font size in pixels."""
        self.size = size
        self.face.set_char_size(size * 64)  # freetype uses 1/64 pixel units

    def get_glyph(self, ch: str) -> Glyph:
        if ch in self._glyph_cache:
            return self._glyph_cache[ch]

        # Load glyph for character
        self.face.load_char(ch)
        glyph_slot = self.face.glyph

        # Extract bitmap data
        bitmap = glyph_slot.bitmap
        w = bitmap.width
        h = bitmap.rows

        # Copy alpha data (freetype bitmap is in 8-bit grayscale)
        alpha = list(bitmap.buffer) if w > 0 and h > 0 else []

        glyph = Glyph(
            w=w,
            h=h,
            x_bearing=glyph_slot.bitmap_left,
            y_bearing=glyph_slot.bitmap_top,
            x_advance=glyph_slot.advance.x >> 6,  # Convert from 1/64 pixels
            y_advance=glyph_slot.advance.y >> 6,
            alpha=alpha
        )

        self._glyph_cache[ch] = glyph
        return glyph

    def measure_text(self, text: str) -> tuple[int, int]:
        """
        Measure the width and height of a text string.

        Returns:
            (width, height) tuple in pixels
        """
        if not text:
            return (0, 0)

        total_width = 0
        min_y = float('inf')
        max_y = float('-inf')

        for ch in text:
            glyph = self.get_glyph(ch)
            total_width += glyph.x_advance

            # Track vertical bounds
            glyph_top = glyph.y_bearing
            glyph_bottom = glyph.y_bearing - glyph.h
            max_y = max(max_y, glyph_top)
            min_y = min(min_y, glyph_bottom)

        if max_y == float('-inf'):
            return (total_width, self.size)

        height = int(max_y - min_y)

        return (total_width, height)

    def clear_cache(self) -> None:
        """Clear the glyph cache."""
        self._glyph_cache.clear()
