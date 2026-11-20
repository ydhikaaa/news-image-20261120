#!/usr/bin/env python3
"""THE WORLD TODAY -- Friday, 20 November 2026.

Draws a broadsheet front page (1024x1024 PNG) summing up the day's world
news. Pure Python 3 standard library only: no network, no clock, no
randomness, no external fonts or images. Every letter is drawn from a
hand-written 5x7 bitmap font defined below, and the PNG is encoded by hand
(zlib + struct). Running it twice produces byte-identical output.
"""
import os
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 242, 231)
INK = (26, 26, 26)
NAVY = (22, 50, 79)
RED = (176, 42, 30)
TEAL = (18, 110, 105)
GOLD = (176, 132, 32)
GREY = (110, 104, 92)
LIGHT = (232, 226, 210)
SEA = (46, 93, 130)
SKY = (214, 228, 238)

# ------------------------------------------------------- 5x7 bitmap font
# Each glyph: 7 rows of 5 bits, '#' = on.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    '*': ("00000", "00100", "10101", "01110", "10101", "00100", "00000"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '<': ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    '>': ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    '_': ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    '\u2022': ("00000", "00000", "01100", "01100", "01100", "00000", "00000"),
    '\u2014': ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
}
UNKNOWN = ("01110", "10001", "10001", "10101", "10001", "10001", "01110")


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        for i in range(w * h):
            self.px[3 * i] = bg[0]
            self.px[3 * i + 1] = bg[1]
            self.px[3 * i + 2] = bg[2]

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = 3 * (y * self.w + x)
            self.px[i] = c[0]
            self.px[i + 1] = c[1]
            self.px[i + 2] = c[2]

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, c)

    def frame(self, x, y, w, h, c, t=1):
        self.rect(x, y, w, t, c)
        self.rect(x, y + h - t, w, t, c)
        self.rect(x, y, t, h, c)
        self.rect(x + w - t, y, t, h, c)

    def hline(self, x0, x1, y, c, t=1):
        for yy in range(y, y + t):
            for xx in range(x0, x1 + 1):
                self.set(xx, yy, c)

    def vline(self, x, y0, y1, c, t=1):
        for xx in range(x, x + t):
            for yy in range(y0, y1 + 1):
                self.set(xx, yy, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            for a in range(t):
                for b in range(t):
                    self.set(x + a, y + b, c)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def disc(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, c)

    def ring(self, cx, cy, r, c, t=2):
        for yy in range(cy - r - t, cy + r + t + 1):
            for xx in range(cx - r - t, cx + r + t + 1):
                d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                if (r - t) ** 2 <= d2 <= r * r:
                    self.set(xx, yy, c)

    def ellipse(self, cx, cy, rx, ry, c):
        for yy in range(cy - ry, cy + ry + 1):
            for xx in range(cx - rx, cx + rx + 1):
                if ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1:
                    self.set(xx, yy, c)


# ------------------------------------------------------------------- text
def text_width(s, scale):
    return len(s) * 6 * scale - scale


def draw_text(cv, x, y, s, scale, color, align="left"):
    w = text_width(s, scale)
    if align == "center":
        x -= w // 2
    elif align == "right":
        x -= w
    cx = x
    for ch in s:
        g = FONT.get(ch.upper(), UNKNOWN) if ch != ' ' else FONT[' ']
        if ch == ' ':
            cx += 6 * scale
            continue
        for r in range(7):
            row = g[r]
            for col in range(5):
                if row[col] == '1' or row[col] == '#':
                    cv.rect(cx + col * scale, y + r * scale, scale, scale, color)
        cx += 6 * scale
    return w


def wrap_text(s, max_w, scale):
    """Greedy word wrap; returns list of lines."""
    words = s.split(' ')
    lines = []
    cur = ''
    for wd in words:
        trial = wd if not cur else cur + ' ' + wd
        if text_width(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def draw_block(cv, x, y, s, max_w, scale, color, line_h=None):
    if line_h is None:
        line_h = 9 * scale
    lines = wrap_text(s, max_w, scale)
    for i, ln in enumerate(lines):
        draw_text(cv, x, y + i * line_h, ln, scale, color)
    return y + len(lines) * line_h


# ------------------------------------------------------------- PNG writer
def write_png(path, cv):
    raw = bytearray()
    stride = cv.w * 3
    for yy in range(cv.h):
        raw.append(0)
        raw.extend(cv.px[yy * stride:(yy + 1) * stride])

    def chunk(typ, data):
        c = struct.pack(">I", len(data)) + typ + data
        c += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
        return c

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 6))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


# ------------------------------------------------------------ illustrations
def draw_cyclone(cv, cx, cy, rmax, color):
    """Spiral storm: three thin arms winding into the eye."""
    import math
    for k in range(3):
        theta = 0.0
        prev = None
        while theta < 4.6 * math.pi:
            r = 5 + (rmax - 5) * (theta / (4.6 * math.pi))
            a = theta + k * 2.1
            x = int(cx + r * math.cos(a))
            y = int(cy + r * math.sin(a) * 0.82)
            if prev is not None:
                cv.line(prev[0], prev[1], x, y, color, 2)
            prev = (x, y)
            theta += 0.22
    cv.disc(cx, cy, 5, PAPER)
    cv.ring(cx, cy, 5, color, 2)


def draw_bat_ball(cv, x, y, s, color):
    # cricket bat: angled blade + handle
    cv.line(x + 8 * s, y + 2 * s, x + 2 * s, y + 12 * s, color, 2 * s)
    cv.line(x + 10 * s, y + 2 * s, x + 4 * s, y + 12 * s, color, 2 * s)
    cv.line(x + 6 * s, y, x + 9 * s, y + 3 * s, color, s)
    cv.disc(x + 16 * s, y + 10 * s, 3 * s, RED)


def draw_globe(cv, cx, cy, r, color):
    cv.ring(cx, cy, r, color, 3)
    cv.ellipse(cx, cy, r, r // 3, color)  # equator band as outline arcs
    cv.rect(cx - r, cy - 1, 2 * r, 2, color)
    cv.line(cx - r // 2, cy - r, cx - r // 2, cy + r, color, 2)
    cv.line(cx + r // 2, cy - r, cx + r // 2, cy + r, color, 2)


def draw_megaphone(cv, x, y, s, color):
    # simple megaphone: cone + handle
    pts = [(x, y + 4 * s), (x + 12 * s, y), (x + 12 * s, y + 8 * s), (x, y + 4 * s)]
    for i in range(len(pts)):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % len(pts)]
        cv.line(x0, y0, x1, y1, color, 2)
    cv.line(x + 3 * s, y + 5 * s, x + 2 * s, y + 10 * s, color, 2)


def draw_reel(cv, cx, cy, r, color):
    cv.ring(cx, cy, r, color, 3)
    cv.disc(cx, cy, 3, color)
    for dx, dy in ((-r // 2, -r // 2), (r // 2, -r // 2), (-r // 2, r // 2),
                   (r // 2, r // 2)):
        cv.disc(cx + dx, cy + dy, 3, color)


def draw_cloud_rain(cv, x, y, s, color):
    cv.ellipse(x + 8 * s, y + 3 * s, 8 * s, 4 * s, color)
    cv.ellipse(x + 4 * s, y + 4 * s, 4 * s, 3 * s, color)
    cv.ellipse(x + 12 * s, y + 4 * s, 4 * s, 3 * s, color)
    for dx in (2, 6, 10, 14):
        cv.line(x + dx * s, y + 8 * s, x + (dx - 1) * s, y + 12 * s, color, 1)


# Dotted world map: coarse landmass grid, 48 x 18.
MAP_ROWS = [
    "                                                ",
    "     #######      ######   ###################  ",
    "   ###########   ############################# ",
    "  ############    ###  ####################### ",
    "  ###########     ###   #####################  ",
    "   ##########            ####  ############     ",
    "    ########             ###   ##########       ",
    "    #######      ###      ##    ########         ",
    "     #####      #####     ##     ######          ",
    "      ###      #######    #      ####            ",
    "      ##       #######           ##              ",
    "       #       ######            #               ",
    "              #####                              ",
    "              ####                               ",
    "              ###        ###                     ",
    "               ##       #####                    ",
    "               #         ###                     ",
    "                          #                      ",
]


def draw_world_map(cv, x, y, cell, color):
    for r, row in enumerate(MAP_ROWS):
        for c, ch in enumerate(row):
            if ch == '#':
                cv.disc(x + c * cell + cell // 2, y + r * cell + cell // 2,
                        max(1, cell // 3), color)


# ------------------------------------------------------------------- page
def draw_page(cv):
    # ---- masthead
    cv.rect(0, 0, W, 6, INK)
    draw_text(cv, W // 2, 20, "THE WORLD TODAY", 8, NAVY, align="center")
    cv.hline(28, W - 28, 92, INK, 2)
    draw_text(cv, 28, 102, "FRIDAY, 20 NOVEMBER 2026", 3, RED)
    draw_text(cv, W - 28, 102, "DRAWN BY A PROGRAM - NO PHOTOS",
              2, GREY, align="right")
    cv.hline(28, W - 28, 128, INK, 3)
    cv.hline(28, W - 28, 133, INK, 1)

    # ---- lead story (left column)
    lx, lw = 28, 576
    y = 148
    draw_text(cv, lx, y, "INDIA - WEATHER", 2, RED)
    y += 30
    y = draw_block(cv, lx, y, "CYCLONE AKVAN BEARS DOWN ON INDIA'S EAST COAST",
                   lw, 5, INK, line_h=42)
    y += 10
    y = draw_block(
        cv, lx, y,
        "Akvan is due to cross the Odisha coast near Gopalpur around "
        "noon today. Winds 90-100 km/h, gusts to 110. Over 105,000 "
        "people moved to 1,224 shelters.",
        lw, 3, INK, line_h=27)
    # illustration: sea + coast + cyclone
    iy = y + 8
    cv.rect(lx, iy, lw, 100, SKY)
    cv.frame(lx, iy, lw, 100, NAVY, 2)
    # land on the right side of the panel
    for k in range(100):
        edge = 330 + int(40 * (k / 100.0)) - int(18 * ((k % 37) / 37.0))
        cv.hline(lx + edge, lx + lw - 2, iy + k, LIGHT, 1)
    cv.line(lx + 330, iy, lx + 352, iy + 100, NAVY, 2)
    draw_cyclone(cv, lx + 190, iy + 50, 42, NAVY)
    draw_text(cv, lx + 8, iy + 8, "BAY OF BENGAL", 2, NAVY)
    draw_text(cv, lx + 420, iy + 30, "ODISHA", 2, RED)
    cv.disc(lx + 470, iy + 58, 4, RED)
    draw_text(cv, lx + 420, iy + 66, "GOPALPUR", 2, INK)
    draw_text(cv, lx + 8, iy + 82, "LANDFALL DUE AROUND NOON", 2, INK)

    # ---- right column: two cards
    rx, rw = 628, 368
    cy = 148
    # card 1: Trump / Iran
    cv.frame(rx, cy, rw, 172, INK, 2)
    cv.rect(rx + 2, cy + 2, rw - 4, 26, NAVY)
    draw_text(cv, rx + 10, cy + 8, "WASHINGTON - IRAN", 2, (255, 255, 255))
    draw_text(cv, rx + 10, cy + 40, "TRUMP: NO RUSH", 4, INK)
    draw_text(cv, rx + 10, cy + 76, "ON IRAN", 4, INK)
    draw_block(cv, rx + 10, cy + 118,
               "\"We'll see what happens after January 1,\" the president "
               "said of renewed strikes.", rw - 20, 2, INK,
               line_h=18)
    cy += 184
    # card 2: cricket
    cv.frame(rx, cy, rw, 172, INK, 2)
    cv.rect(rx + 2, cy + 2, rw - 4, 26, TEAL)
    draw_text(cv, rx + 10, cy + 8, "WELLINGTON - DAY 2", 2, (255, 255, 255))
    draw_text(cv, rx + 10, cy + 40, "NICHOLLS 146*", 4, INK)
    draw_text(cv, rx + 10, cy + 76, "NZ 317-6", 4, INK)
    draw_block(cv, rx + 10, cy + 118,
               "Nicholls and Phillips put on 216 after NZ fell to 70-5; "
               "Phillips made 118.",
               rw - 20, 2, INK, line_h=18)
    draw_bat_ball(cv, rx + rw - 46, cy + 2, 1, (255, 255, 255))

    # ---- by the numbers strip
    ny = 560
    cv.rect(28, ny, W - 56, 66, NAVY)
    draw_text(cv, 44, ny + 8, "BY THE NUMBERS", 2, GOLD)
    stats = [("105,304", "EVACUATED"), ("110", "KM/H GUSTS"),
             ("317-6", "NZ AT LUNCH"), ("146*", "NICHOLLS"),
             ("216", "RUN STAND"), ("300+", "SCHOOLS ON STRIKE")]
    sx = 44
    for big, lab in stats:
        draw_text(cv, sx, ny + 26, big, 3, (255, 255, 255))
        draw_text(cv, sx, ny + 50, lab, 1, (200, 205, 210))
        sx += 162

    # ---- four story cards
    cards = [
        ("COP31 - ANTALYA", "CLIMATE TALKS END",
         "The UN climate conference in Antalya reaches its scheduled "
         "close today.", "globe"),
        ("EUROPE", "STUDENTS WALK OUT",
         "Tens of thousands strike at 300+ schools in 100+ towns "
         "against war.", "megaphone"),
        ("GOA - INDIA", "IFFI OPENS IN GOA",
         "The 57th film festival of India opens today and runs to "
         "28 November.", "reel"),
        ("FLORIDA - USA", "FLORIDA FLOOD WATCH",
         "Blizzard Beach closed as a flood watch covers Orlando; "
         "4-6 in of rain due.", "cloud"),
    ]
    cx0, cw, gap = 28, 226, 12
    cy0, ch = 638, 178
    for i, (kick, head, body, icon) in enumerate(cards):
        x = cx0 + i * (cw + gap)
        cv.frame(x, cy0, cw, ch, INK, 2)
        cv.rect(x + 2, cy0 + 2, cw - 4, 24, RED if i % 2 == 0 else NAVY)
        draw_text(cv, x + 8, cy0 + 8, kick, 1, (255, 255, 255))
        if icon == "globe":
            draw_globe(cv, x + cw - 18, cy0 + 14, 8, (255, 255, 255))
        elif icon == "megaphone":
            draw_megaphone(cv, x + cw - 32, cy0 + 6, 1, (255, 255, 255))
        elif icon == "reel":
            draw_reel(cv, x + cw - 18, cy0 + 14, 8, (255, 255, 255))
        else:
            draw_cloud_rain(cv, x + cw - 34, cy0 + 4, 1, (255, 255, 255))
        hy = cy0 + 34
        hy = draw_block(cv, x + 10, hy, head, cw - 20, 3, INK, line_h=26)
        draw_block(cv, x + 10, hy + 6, body, cw - 20, 2, INK, line_h=17)

    # ---- children's day banner
    cb = 824
    cv.rect(28, cb, W - 56, 24, LIGHT)
    draw_text(cv, W // 2, cb + 5,
              "WORLD CHILDREN'S DAY - \"MY DAY. MY RIGHTS. MY FUTURE.\" - UNICEF",
              2, TEAL, align="center")

    # ---- world map strip
    my = 856
    cv.hline(28, W - 28, my, INK, 2)
    draw_text(cv, 28, my + 8, "AROUND THE WORLD", 3, INK)
    draw_text(cv, W - 28, my + 8, "FRIDAY 20 NOVEMBER 2026", 2, GREY,
              align="right")
    mx, myy = 48, 888
    draw_world_map(cv, mx, myy, 6, NAVY)
    pins = [(35, 8, "1"), (45, 16, "2"), (26, 6, "3"), (34, 9, "4"),
            (8, 8, "5"), (24, 4, "6")]
    for col, row, n in pins:
        px = mx + col * 6 + 3
        py = myy + row * 6 + 3
        cv.disc(px, py, 7, RED)
        draw_text(cv, px - 3, py - 5, n, 1, (255, 255, 255))
    legend = [
        ("1", "ODISHA - CYCLONE AKVAN"),
        ("2", "WELLINGTON - NZ 317-6"),
        ("3", "ANTALYA - COP31 CLOSES"),
        ("4", "GOA - FILM FESTIVAL"),
        ("5", "FLORIDA - FLOOD WATCH"),
        ("6", "EUROPE - YOUTH STRIKE"),
    ]
    for i, (n, txt) in enumerate(legend):
        lx2 = 420 if i % 2 == 0 else 720
        ly = 896 + (i // 2) * 30
        cv.disc(lx2, ly + 5, 8, RED)
        draw_text(cv, lx2 - 3, ly - 1, n, 1, (255, 255, 255))
        draw_text(cv, lx2 + 16, ly - 1, txt, 2, INK)

    # ---- ticker
    ty = 998
    cv.rect(0, ty, W, 24, INK)
    draw_text(cv, 14, ty + 5,
              "PAKISTAN PETROL +Rs1 TO Rs323  •  ASX 200 FUTURES -1%  •  "
              "COP31 FINAL DAY",
              2, (255, 255, 255))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "./out")
    os.makedirs(out_dir, exist_ok=True)
    cv = Canvas(W, H, PAPER)
    draw_page(cv)
    write_png(os.path.join(out_dir, "entry.png"), cv)


if __name__ == "__main__":
    main()
