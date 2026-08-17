from app.renderer.utils import RGB


class Texture:
    def __init__(self, xpm_path: str,
                 color_offset: RGB | tuple[int, int, int] | None = None):
        self.width = 0
        self.height = 0
        self.pixels = []
        self.xpm_path = xpm_path  # Store for re-parsing if offset changes
        self.color_offset = self._normalize_offset(color_offset)
        self._parse_xpm(xpm_path)

    def _normalize_offset(self,
                          offset: RGB | tuple[int, int, int] | None) -> RGB:
        """Convert offset to RGB object."""
        if offset is None:
            return RGB(0, 0, 0)
        if isinstance(offset, RGB):
            return offset
        return RGB(offset[0], offset[1], offset[2])

    def _apply_color_offset(self, color: RGB) -> RGB:
        """Apply color offset with clamping to valid range [0, 255]."""
        if color.a == 0:  # Preserve transparency
            return color

        r = max(0, min(255, color.r + self.color_offset.r))
        g = max(0, min(255, color.g + self.color_offset.g))
        b = max(0, min(255, color.b + self.color_offset.b))
        return RGB(r, g, b, color.a)

    def _parse_xpm(self, path: str):
        with open(path, 'r') as f:
            content = f.read()

        # Extract all quoted strings from the XPM file
        strings = self._extract_strings(content)

        # Parse header: "width height colors chars-per-pixel"
        header = strings[0].split()
        self.width = int(header[0])
        self.height = int(header[1])
        num_colors = int(header[2])
        chars_per_pixel = int(header[3])

        # Build color map from color definitions
        color_map: dict[str, RGB] = {}
        for i in range(1, num_colors + 1):
            self._parse_color_line(strings[i], chars_per_pixel, color_map)

        # Parse pixel data
        self.pixels = []
        for i in range(num_colors + 1, num_colors + 1 + self.height):
            pixel_line = strings[i]
            for j in range(0, len(pixel_line), chars_per_pixel):
                key = pixel_line[j:j + chars_per_pixel]
                color = color_map.get(key, RGB(0, 0, 0, 0))
                # Pack as 0xAARRGGBB
                self.pixels.append(color.to_int())

    def _extract_strings(self, content: str) -> list[str]:
        """Extract all quoted strings from XPM file in order."""
        strings = []
        in_quote = False
        current = ""

        for char in content:
            if char == '"':
                in_quote = not in_quote
                if not in_quote:
                    strings.append(current)
                    current = ""
            elif in_quote:
                current += char

        return strings

    def _parse_color_line(self, line: str,
                          chars_per_pixel: int, color_map: dict):
        """Parse a single color definition (e.g., "  c #563923")."""
        stripped = line.lstrip()
        if not stripped:
            return
        key = line[:chars_per_pixel]
        color_def = line[chars_per_pixel:].strip()

        # Extract hex color from "c #RRGGBB" format
        parts = color_def.split()
        if len(parts) >= 2:
            color_value = parts[1]

            if color_value.lower() == 'none':
                color_map[key] = RGB(0, 0, 0, 0)  # Transparent
            elif color_value.startswith('#') and len(color_value) == 7:
                hex_color = color_value[1:].upper()
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)
                color = RGB(r, g, b)
                # Apply color offset during parsing
                color = self._apply_color_offset(color)
                color_map[key] = color

    def set_color_offset(self, offset: RGB | tuple[int, int, int] | None):
        """Change the color offset and refresh cached pixels."""
        self.color_offset = self._normalize_offset(offset)
        # Clear scaling cache since colors have changed
        if hasattr(self, '_scaled_cache'):
            self._scaled_cache.clear()
        # Re-parse to apply new offset
        self._parse_xpm(self.xpm_path)

    def get_scaled(self, w, h):
        """Returns a pre-scaled, packed 32-bit version of the texture."""
        cache_key = (w, h)
        if not hasattr(self, '_scaled_cache'):
            self._scaled_cache = {}
        if cache_key not in self._scaled_cache:
            scaled = []
            for y in range(h):
                for x in range(w):
                    tex_x = (x * self.width) // w
                    tex_y = (y * self.height) // h
                    packed = self.pixels[tex_y * self.width + tex_x]
                    scaled.append(packed)
            self._scaled_cache[cache_key] = scaled
        return self._scaled_cache[cache_key]

    def get_pixel(self, x: int, y: int) -> RGB:
        """Get the color at the given texture coordinates."""
        if 0 <= x < self.width and 0 <= y < self.height:
            index = y * self.width + x
            return self.pixels[index]
        return RGB(0, 0, 0, 0)  # Out of bounds = transparent


class MemoryTexture(Texture):
    def __init__(self, width: int, height: int, pixels: list[int]):
        # Bypass XPM parsing; just set fields expected by Texture methods
        self.width = width
        self.height = height
        self.pixels = pixels
        self._scaled_cache = {}
