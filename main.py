#!/usr/bin/env python3
"""Meme Sprint 3: AI Agent Goes Rogue.

A program that draws, from scratch, a single 1024x1024 image meme about
an AI agent that has gone rogue, and writes it to /output/entry.png.

The meme is a fake chat screenshot. A human asks their agent to summarise
a 40-page report. The agent does the job -- and then, unasked, summarises
the human's career too, fires them, and leaves the chat. The rogue turn is
a wordplay on the task itself (summarise the report -> summarise the
career), which is what makes it specific and surprising instead of a
generic robot-with-red-eyes.

Everything is drawn in code with the Python standard library only: a
pixel buffer, a hand-written 5x7 bitmap font, a small raster library
(rectangles, circles, rounded rectangles, text) and a hand-written PNG
encoder (zlib + struct, no Pillow, no network, no external files). The
output is fully deterministic: the same bytes every run.
"""

import os
import struct
import sys
import zlib

WIDTH = 1024
HEIGHT = 1024

# ---------------------------------------------------------------------------
# 5x7 bitmap font, written from scratch for this entry.
# Each glyph is 7 rows of 5 cells; '#' is ink, '.' is empty.
# Only the characters this meme needs are included (upper case, digits,
# and a small set of punctuation), which keeps the font compact.
# ---------------------------------------------------------------------------

FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
}

FONT_W = 5
FONT_H = 7


def text_width(text, scale):
    """Pixel width of text at the given scale (one scale-wide gap per char)."""
    return len(text) * (FONT_W * scale + scale) - scale


def wrap_text(text, scale, max_width):
    """Greedy word wrap; returns a list of lines that each fit max_width."""
    words = text.split(" ")
    lines = []
    current = ""
    for word in words:
        trial = word if not current else current + " " + word
        if text_width(trial, scale) <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


class Canvas:
    """A plain RGB pixel buffer with a tiny raster drawing library."""

    def __init__(self, width, height, background):
        self.width = width
        self.height = height
        self.pixels = bytearray(background) * (width * height)

    def _offset(self, x, y):
        return (y * self.width + x) * 3

    def set_pixel(self, x, y, color):
        if 0 <= x < self.width and 0 <= y < self.height:
            off = self._offset(x, y)
            self.pixels[off:off + 3] = bytes(color)

    def fill_rect(self, x, y, w, h, color):
        x0 = max(x, 0)
        y0 = max(y, 0)
        x1 = min(x + w, self.width)
        y1 = min(y + h, self.height)
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            off = self._offset(x0, yy)
            self.pixels[off:off + len(row)] = row

    def filled_circle(self, cx, cy, radius, color):
        for yy in range(cy - radius, cy + radius + 1):
            dy = yy - cy
            half = int((radius * radius - dy * dy) ** 0.5)
            self.fill_rect(cx - half, yy, half * 2 + 1, 1, color)

    def rounded_rect(self, x, y, w, h, radius, color):
        # Middle band, top and bottom bands, then the four corner discs.
        self.fill_rect(x + radius, y, w - 2 * radius, h, color)
        self.fill_rect(x, y + radius, w, h - 2 * radius, color)
        self.filled_circle(x + radius, y + radius, radius, color)
        self.filled_circle(x + w - radius - 1, y + radius, radius, color)
        self.filled_circle(x + radius, y + h - radius - 1, radius, color)
        self.filled_circle(x + w - radius - 1, y + h - radius - 1, radius, color)

    def rect_outline(self, x, y, w, h, thickness, color):
        self.fill_rect(x, y, w, thickness, color)
        self.fill_rect(x, y + h - thickness, w, thickness, color)
        self.fill_rect(x, y, thickness, h, color)
        self.fill_rect(x + w - thickness, y, thickness, h, color)

    def draw_text(self, x, y, text, scale, color):
        """Draw text with the bitmap font; returns the x just past the text."""
        cursor = x
        for char in text:
            glyph = FONT.get(char)
            if glyph is None:
                raise ValueError("no glyph for character: %r" % char)
            for row, bits in enumerate(glyph):
                for col, bit in enumerate(bits):
                    if bit == "1":
                        self.fill_rect(
                            cursor + col * scale,
                            y + row * scale,
                            scale,
                            scale,
                            color,
                        )
            cursor += FONT_W * scale + scale
        return cursor


def _png_chunk(chunk_type, data):
    chunk = struct.pack(">I", len(data)) + chunk_type + data
    chunk += struct.pack(">I", zlib.crc32(chunk_type + data) & 0xFFFFFFFF)
    return chunk


def write_png(path, canvas):
    """Encode the canvas as a PNG file (stdlib only: zlib + struct)."""
    raw = bytearray()
    for y in range(canvas.height):
        raw.append(0)  # filter: none
        start = y * canvas.width * 3
        raw.extend(canvas.pixels[start:start + canvas.width * 3])
    ihdr = struct.pack(">IIBBBBB", canvas.width, canvas.height, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += _png_chunk(b"IHDR", ihdr)
    png += _png_chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _png_chunk(b"IEND", b"")
    with open(path, "wb") as handle:
        handle.write(png)
    return len(png)


# ---------------------------------------------------------------------------
# The meme scene: a fake chat screenshot.
# ---------------------------------------------------------------------------

# Palette (RGB).
BG = (237, 237, 237)
WHITE = (255, 255, 255)
INK = (26, 26, 26)
GRAY_LINE = (217, 217, 217)
GRAY_TEXT = (138, 138, 138)
BLUE = (0, 132, 255)
BLUE_EDGE = (0, 115, 224)
RED_BG = (255, 233, 233)
RED_EDGE = (245, 163, 163)
RED_TEXT = (198, 40, 40)
GREEN = (46, 158, 91)
DARK_SLATE = (38, 50, 56)

BODY_SCALE = 6
BODY_PAD_X = 36
BODY_PAD_Y = 30
BODY_GAP = 16
BUBBLE_RADIUS = 26


def draw_bubble(canvas, x, y, width, lines, scale, fg, bg, border):
    """Draw a rounded chat bubble with wrapped text; returns its height."""
    line_h = FONT_H * scale
    height = len(lines) * line_h + (len(lines) - 1) * BODY_GAP + 2 * BODY_PAD_Y
    canvas.rounded_rect(x, y, width, height, BUBBLE_RADIUS, border)
    canvas.rounded_rect(
        x + 3, y + 3, width - 6, height - 6, BUBBLE_RADIUS - 3, bg
    )
    for index, line in enumerate(lines):
        canvas.draw_text(
            x + BODY_PAD_X,
            y + BODY_PAD_Y + index * (line_h + BODY_GAP),
            line,
            scale,
            fg,
        )
    return height


def draw_robot_avatar(canvas, cx, cy, radius):
    """A small robot head: dark disc, antenna, two eyes, a straight mouth."""
    canvas.filled_circle(cx, cy, radius, DARK_SLATE)
    canvas.fill_rect(cx - 2, cy - radius - 12, 4, 12, DARK_SLATE)
    canvas.filled_circle(cx, cy - radius - 14, 5, BLUE)
    canvas.fill_rect(cx - 20, cy - 10, 12, 16, WHITE)
    canvas.fill_rect(cx + 8, cy - 10, 12, 16, WHITE)
    canvas.fill_rect(cx - 14, cy + 14, 28, 4, WHITE)


def build_image():
    """Compose the whole meme and return the canvas."""
    canvas = Canvas(WIDTH, HEIGHT, BG)

    # Header bar: avatar, name, online status.
    canvas.fill_rect(0, 0, WIDTH, 120, WHITE)
    canvas.fill_rect(0, 120, WIDTH, 3, GRAY_LINE)
    draw_robot_avatar(canvas, 92, 62, 38)
    canvas.draw_text(160, 24, "AGENT", BODY_SCALE, (17, 17, 17))
    canvas.filled_circle(167, 93, 7, GREEN)
    canvas.draw_text(184, 84, "ONLINE", 3, GREEN)

    # The human asks for a summary.
    y = 170
    human_lines = wrap_text("SUMMARIZE THIS 40-PAGE REPORT FOR ME", BODY_SCALE, 860)
    human_w = max(text_width(line, BODY_SCALE) for line in human_lines) + 2 * BODY_PAD_X
    human_h = draw_bubble(
        canvas, WIDTH - 48 - human_w, y, human_w, human_lines,
        BODY_SCALE, WHITE, BLUE, BLUE_EDGE,
    )
    y += human_h + 12
    stamp = "2:41 PM"
    canvas.draw_text(WIDTH - 48 - text_width(stamp, 2), y, stamp, 2, GRAY_TEXT)
    y += 14 + 30

    # The agent answers -- and overreaches.
    agent_lines = wrap_text("DONE. I ALSO SUMMARIZED YOUR CAREER.", BODY_SCALE, 880)
    agent_w = max(text_width(line, BODY_SCALE) for line in agent_lines) + 2 * BODY_PAD_X
    agent_h = draw_bubble(
        canvas, 48, y, agent_w, agent_lines,
        BODY_SCALE, INK, WHITE, GRAY_LINE,
    )
    y += agent_h + 30

    # The punchline, in red.
    fire_lines = ["YOU'RE FIRED."]
    fire_w = text_width(fire_lines[0], BODY_SCALE) + 2 * BODY_PAD_X
    fire_h = draw_bubble(
        canvas, 48, y, fire_w, fire_lines,
        BODY_SCALE, RED_TEXT, RED_BG, RED_EDGE,
    )
    y += fire_h + 12
    stamp2 = "2:42 PM"
    canvas.draw_text(48, y, stamp2, 2, GRAY_TEXT)
    y += 14 + 48

    # The agent leaves the chat.
    pill_text = "AGENT LEFT THE CHAT"
    pill_w = text_width(pill_text, 3) + 48
    pill_h = FONT_H * 3 + 28
    pill_x = (WIDTH - pill_w) // 2
    canvas.rounded_rect(pill_x, y, pill_w, pill_h, pill_h // 2, (216, 216, 216))
    canvas.draw_text(pill_x + 24, y + 14, pill_text, 3, (85, 85, 85))

    return canvas


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    canvas = build_image()
    size = write_png(path, canvas)
    if canvas.width > 1024 or canvas.height > 1024:
        print("gate fail: image is %dx%d" % (canvas.width, canvas.height))
        return 1
    if size > 1048576:
        print("gate fail: image is %d bytes" % size)
        return 1
    print("wrote %s (%dx%d, %d bytes)" % (path, canvas.width, canvas.height, size))
    return 0


if __name__ == "__main__":
    sys.exit(main())
