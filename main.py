#!/usr/bin/env python3
"""THE WORLD TODAY - a one-page broadsheet of Friday 20 November 2026.

Pure Python standard library. Renders a newspaper front page summarising
the world news of 20 November 2026 and writes it to
$MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png).
Deterministic: the same bytes on every run.
"""

import math
import os
import struct
import zlib

# ---------------------------------------------------------------- PNG writer

def _chunk(tag, data):
    out = struct.pack(">I", len(data)) + tag + data
    out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    return out


def save_png(canvas, path):
    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)
        raw += canvas.px[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n"
           + _chunk(b"IHDR", ihdr)
           + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
           + _chunk(b"IEND", b""))
    with open(path, "wb") as fh:
        fh.write(png)

# ------------------------------------------------------------------- colours

PAPER = (250, 247, 238)
PANEL = (255, 253, 247)
INK = (18, 18, 18)
GREY = (96, 92, 84)
RED = (146, 26, 22)
BLUE = (38, 66, 108)
GREEN = (26, 102, 52)
SEA = (226, 233, 238)

# ------------------------------------------------------------- 5x7 pixel font
# Each glyph: 7 rows of 5 pixels, '#' = ink, '.' = blank, rows joined by '/'.

FONT = {
    "A": ".###./#...#/#...#/#####/#...#/#...#/#...#",
    "B": "####./#...#/#...#/####./#...#/#...#/####.",
    "C": ".####/#..../#..../#..../#..../#..../.####",
    "D": "####./#...#/#...#/#...#/#...#/#...#/####.",
    "E": "#####/#..../#..../####./#..../#..../#####",
    "F": "#####/#..../#..../####./#..../#..../#....",
    "G": ".####/#..../#..../#.###/#...#/#...#/.###.",
    "H": "#...#/#...#/#...#/#####/#...#/#...#/#...#",
    "I": "#####/..#../..#../..#../..#../..#../#####",
    "J": "..###/...#./...#./...#./...#./#..#./.##..",
    "K": "#...#/#..#./#.#../##.../#.#../#..#./#...#",
    "L": "#..../#..../#..../#..../#..../#..../#####",
    "M": "#...#/##.##/#.#.#/#.#.#/#...#/#...#/#...#",
    "N": "#...#/##..#/##..#/#.#.#/#..##/#..##/#...#",
    "O": ".###./#...#/#...#/#...#/#...#/#...#/.###.",
    "P": "####./#...#/#...#/####./#..../#..../#....",
    "Q": ".###./#...#/#...#/#...#/#.#.#/#..#./.##.#",
    "R": "####./#...#/#...#/####./#.#../#..#./#...#",
    "S": ".####/#..../#..../.###./....#/....#/####.",
    "T": "#####/..#../..#../..#../..#../..#../..#..",
    "U": "#...#/#...#/#...#/#...#/#...#/#...#/.###.",
    "V": "#...#/#...#/#...#/#...#/#...#/.#.#./..#..",
    "W": "#...#/#...#/#...#/#.#.#/#.#.#/##.##/#...#",
    "X": "#...#/.#.#./..#../..#../..#../.#.#./#...#",
    "Y": "#...#/#...#/.#.#./..#../..#../..#../..#..",
    "Z": "#####/....#/..##./..#../.#.../#..../#####",
    "a": "...../...../.####/....#/.####/#...#/.####",
    "b": "#..../#..../####./#...#/#...#/#...#/####.",
    "c": "...../...../.####/#..../#..../#..../.####",
    "d": "....#./....#./.####/#...#/#...#/#...#/.####",
    "e": "...../...../.###./#...#/#####/#..../.###.",
    "f": "..##./.#.../.#.../####./.#.../.#.../.#...",
    "g": "...../...../.####/#...#/.####/....#/.###.",
    "h": "#..../#..../####./#...#/#...#/#...#/#...#",
    "i": "..#../...../.##../..#../..#../..#../.###.",
    "j": "...#./...../..##./...#/....#/....#/.##..",
    "k": "#..../#..../#..#./#.#../##.../#.#../#..#.",
    "l": ".##../..#../..#../..#../..#../..#../.###.",
    "m": "...../...../##.#./#.#.#/#.#.#/#.#.#/#.#.#",
    "n": "...../...../####./#...#/#...#/#...#/#...#",
    "o": "...../...../.###./#...#/#...#/#...#/.###.",
    "p": "...../...../####./#...#/####./#..../#....",
    "q": "...../...../.####/#...#/.####/....#/....#",
    "r": "...../...../#.##./##..#/#..../#..../#....",
    "s": "...../...../.####/#..../.###./....#/####.",
    "t": ".#.../.#.../####./.#.../.#.../.#.../..##.",
    "u": "...../...../#...#/#...#/#...#/#..##/.##.#",
    "v": "...../...../#...#/#...#/#...#/.#.#./..#..",
    "w": "...../...../#...#/#.#.#/#.#.#/#.#.#/.#.#.",
    "x": "...../...../#...#/.#.#./..#../.#.#./#...#",
    "y": "...../...../#...#/#...#/.####/....#/.###.",
    "z": "...../...../#####/...#./..#../.#.../#####",
    "0": ".###./#..##/#.#.#/##..#/#...#/#...#/.###.",
    "1": "..#../.##../..#../..#../..#../..#../#####",
    "2": ".###./#...#/....#/..##./.#.../#..../#####",
    "3": "####./....#/....#/.###./....#/....#/####.",
    "4": "...#./..##./.#.#./#..#/#####/...#./...#.",
    "5": "#####/#..../####./....#/....#/#...#/.###.",
    "6": ".###./#..../#..../####./#...#/#...#/.###.",
    "7": "#####;....#;....#;...#.;...#.;..#..;..#..",
    "8": ".###./#...#/#...#/.###./#...#/#...#/.###.",
    "9": ".###./#...#/#...#/.####/....#/....#/.###.",

    " ": ".....;.....;.....;.....;.....;.....;.....",
    ".": ".....;.....;.....;.....;.....;.##..;.##..",
    ",": ".....;.....;.....;.....;.##..;.##..;.#...",
    ";": ".....;.##..;.##..;.....;.##..;.##..;.#...",
    ":": ".....;.##..;.##..;.....;.##..;.##..;.....",
    "'": ".##..;.##..;.#...;.....;.....;.....;.....",
    '"': ".#.#.;.#.#.;.....;.....;.....;.....;.....",

    "(": "..##.;.#...;.#...;.#...;.#...;.#...;..##.",
    ")": ".##..;...#.;...#.;...#.;...#.;...#.;.##..",
    "%": "##..#;##.#.;...#.;..#..;.#...;#..##;#..##",
    "+": ".....;..#..;..#..;#####;..#..;..#..;.....",
    "/": "....#;....#;...#.;..#..;.#...;#....;#....",
    "&": ".##..;#..#.;#.#..;.#...;#.#.#;#..#.;.##.#",
    "·": ".....;.....;.....;.##..;.##..;.....;.....",

    "!": "..#..;..#..;..#..;..#..;..#..;.....;..#..",
    "?": ".###.;#...#;....#;..##.;..#..;.....;..#..",
    "$": "..#..;.####;#.#..;.###.;..#.#;####.;..#..",
    "-": ".....;.....;.....;#####;.....;.....;.....",
    "–": ".....;.....;.....;#####;.....;.....;.....",
    "—": ".....;.....;.....;#####;.....;.....;.....",
    "•": ".....;.....;.###.;.###.;.###.;.....;.....",
    "*": ".....;.#.#.;..#..;#####;..#..;.#.#.;.....",
}


def _cells(raw):
    rows = raw.replace(";", "/").split("/")
    pts = []
    for gy, row in enumerate(rows):
        for gx, ch in enumerate(row):
            if ch == "#":
                pts.append((gx, gy))
    return pts


GLYPH_CELLS = {ch: _cells(raw) for ch, raw in FONT.items()}
FALLBACK = _cells(FONT["?"])


# -------------------------------------------------------------------- canvas

class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg) * (w * h)

    def rect(self, x, y, rw, rh, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + rw)
        y1 = min(self.h, y + rh)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        n = len(row)
        for yy in range(y0, y1):
            off = (yy * self.w + x0) * 3
            self.px[off:off + n] = row

    def hline(self, x, y, length, color, thick=1):
        self.rect(x, y, length, thick, color)

    def vline(self, x, y, length, color, thick=1):
        self.rect(x, y, thick, length, color)

    def frame(self, x, y, rw, rh, color, thick=2):
        self.hline(x, y, rw, color, thick)
        self.hline(x, y + rh - thick, rw, color, thick)
        self.vline(x, y, rh, color, thick)
        self.vline(x + rw - thick, y, rh, color, thick)


# ---------------------------------------------------------------------- text

def text_width(s, scale, tracking):
    if not s:
        return 0
    return len(s) * (5 * scale + tracking) - tracking


def draw_text(cv, x, y, s, scale=2, color=INK, bold=False, tracking=None):
    if tracking is None:
        tracking = max(1, scale // 2)
    step = 5 * scale + tracking
    extra = max(1, scale // 2) if bold else 0
    cx = x
    for ch in s:
        cells = GLYPH_CELLS.get(ch, FALLBACK)
        for gx, gy in cells:
            cv.rect(cx + gx * scale, y + gy * scale, scale + extra,
                    scale, color)
        cx += step
    return cx - tracking


def wrap(text, max_width, scale=2, tracking=None):
    if tracking is None:
        tracking = max(1, scale // 2)
    lines = []
    cur = ""
    for word in text.split():
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale, tracking) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(cv, x, y, text, max_width, scale=2, color=INK,
                 line_height=19, tracking=None):
    for line in wrap(text, max_width, scale, tracking):
        draw_text(cv, x, y, line, scale, color, tracking=tracking)
        y += line_height
    return y


def draw_centered(cv, cx, y, s, scale=2, color=INK, bold=False,
                  tracking=None):
    if tracking is None:
        tracking = max(1, scale // 2)
    w = text_width(s, scale, tracking)
    draw_text(cv, cx - w // 2, y, s, scale, color, bold, tracking)
    return w


def kicker(cv, x, y, s, color=RED):
    draw_text(cv, x, y, s, 2, color, bold=True, tracking=2)
    return y + 22


def headline(cv, x, y, lines, scale=3, color=INK, line_height=None):
    if line_height is None:
        line_height = 7 * scale + 7
    for line in lines:
        draw_text(cv, x, y, line, scale, color, bold=True,
                  tracking=max(1, scale // 2))
        y += line_height
    return y


# ------------------------------------------------------------------- content
# Every fact below was reported on Friday 20 November 2026 (IMD bulletins,
# BBC, UN News, Al Jazeera, The Guardian, France 24, CNBC, NASA and others).

LEAD_BODY = (
    "The International Court of Justice ruled that Myanmar committed "
    "genocide against its Rohingya minority - the first time the court "
    "has held a state responsible for genocide. The judges voted nine "
    "to six in the case brought by The Gambia over the 2017 military "
    "crackdown that killed thousands and drove hundreds of thousands "
    "into Bangladesh. More than 1.3 million Rohingya remain displaced, "
    "and questions remain over how the judgment will be enforced."
)

CYCLONE_BODY = (
    "Akvan crossed the coast close to Gopalpur on Friday morning and "
    "weakened into a deep depression over Odisha. Officials reported "
    "no deaths and no major damage in the first assessments, and "
    "heavy rain was forecast for south Bengal into Saturday morning."
)

CYCLONE_FACTS = [
    "WINDS 70-80 KM/H, GUSTS 90",
    "LANDFALL 07:30-08:30 IST",
    "COMPLETE BY 11:20 IST",
    "300,000+ PEOPLE EVACUATED",
    "NO DEATHS REPORTED",
    "RAIN: PATAPUR 209 MM",
]
SUMMIT_BODY = (
    "Presidents Trump, Xi and Putin held their first three-way "
    "summit in Shenzhen and signed a four-point declaration on "
    "nuclear risk, UN reform, energy and the ICC."
)

MARKETS_BODY = (
    "Anthropic closed 17% above its $83 offer price in a record "
    "$81.3 billion Nasdaq debut, but it did not revive a weak "
    "AI trade."
)

MARKET_MOVES = [
    ("ANTHROPIC", 17.0, "+17%"),
    ("NIKKEI 225", -4.8, "-4.8%"),
    ("SOFTBANK", -16.0, "-16%"),
]

KYIV_BODY = (
    "A fresh Russian missile attack hit Kyiv on Friday, a day after "
    "strikes killed one person and damaged a cathedral and the "
    "Austrian and Dutch embassies. Ukraine struck the Kerch Bridge "
    "to Crimea for the third time in four days, halting rail "
    "traffic, and Putin vowed a painful response. In Berlin, "
    "Ukraine's allies said Europe has a united position for talks "
    "with Russia."
)

COP_BODY = (
    "Negotiators in Antalya dropped any call to phase out fossil "
    "fuels from a slimmed-down draft deal as COP31 entered its "
    "final day."
)

EU_BODY = (
    "Britain and the European Union sealed a reset agreement at "
    "their Brussels summit, covering youth mobility, food trade and "
    "carbon emissions - the deepest rebuilding of ties since Brexit."
)

HOUTHI_BODY = (
    "Houthi missiles damaged the Public Investment Fund tower in "
    "Riyadh's financial district. No injuries were reported."
)

NVIDIA_BODY = (
    "California's attorney general subpoenaed Nvidia over whether "
    "advanced chips or confidential data reached China, after chief "
    "executive Jensen Huang resigned. Interim CEO Colette Kress "
    "urged staff to move forward. The probe could tighten US export "
    "controls on AI chips."
)

BRIEFS = [
    "HAITI - Police say 34 suspected gang members killed in "
    "Martissant raid.",
    "SENEGAL - Dozens missing after migrant boat capsizes; "
    "4 bodies found.",
    "SPACE - Voyager 1 reaches one light-day from Earth, "
    "49 years on.",
    "SPORT - Houston rout Indianapolis 26-3; Nacua suspended "
    "3 games.",
]


# -------------------------------------------------------------------- layout

def draw_spiral(cv, cx, cy, max_r):
    steps = 340
    for i in range(steps):
        t = i / 20.0
        r = 4.0 + (max_r - 4.0) * (t / (steps / 20.0))
        x = cx + int(r * math.cos(t))
        y = cy + int(r * math.sin(t) * 0.84)
        cv.rect(x - 3, y - 3, 7, 7, BLUE)
    cv.rect(cx - 6, cy - 6, 13, 13, RED)
    for k in range(5):
        wx = cx - max_r - 12 + k * (2 * max_r + 24) // 5
        for s in range(16):
            yy = cy + max_r + 16 + int(3 * math.sin(s / 2.4 + k))
            cv.rect(wx + s * 2, yy, 2, 2, BLUE)


def draw_front_page():
    cv = Canvas(1024, 1024, PAPER)
    left = 36
    right = 988
    width = right - left

    # masthead block
    cv.hline(left, 24, width, INK, 4)
    cv.hline(left, 31, width, INK, 1)
    draw_text(cv, left, 40, "FULL-DAY EDITION", 2, GREY, tracking=2)
    r = "FRIDAY 20 NOVEMBER 2026"
    draw_text(cv, right - text_width(r, 2, 2), 40, r, 2, GREY,
              tracking=2)
    draw_centered(cv, 512, 62, "THE WORLD TODAY", 9, INK, bold=True,
                  tracking=6)
    cv.hline(left, 133, width, INK, 1)
    draw_centered(cv, 512, 141, "THE WORLD'S NEWS OF FRIDAY, "
                  "20 NOVEMBER 2026 - IN ONE PAGE", 2, INK, tracking=2)
    cv.hline(left, 163, width, INK, 4)

    # lead story, left
    y = kicker(cv, left, 178, "INTERNATIONAL JUSTICE - THE HAGUE")
    y = headline(cv, left, y + 2,
                 ["WORLD COURT: MYANMAR", "COMMITTED GENOCIDE",
                  "AGAINST THE ROHINGYA"],
                 scale=4, line_height=38)
    y = draw_wrapped(cv, left, y + 6, LEAD_BODY, 576, 2, INK, 17)
    lead_end = y

    # cyclone panel, right
    px, pw = 640, 348
    cv.rect(px, 178, pw, 330, PANEL)
    cv.frame(px, 178, pw, 330, INK, 2)
    draw_centered(cv, px + pw // 2, 190, "CYCLONE AKVAN", 3, RED,
                  bold=True, tracking=3)
    draw_spiral(cv, px + pw // 2, 268, 38)
    hy = headline(cv, px + 16, 330,
                  ["STORM SLAMS ASHORE", "AT GOPALPUR, THEN"],
                  scale=3, line_height=24)
    draw_text(cv, px + 16, hy, "WEAKENS OVER ODISHA", 3, INK, bold=True,
              tracking=1)
    fy = hy + 32
    for fact in CYCLONE_FACTS:
        draw_text(cv, px + 16, fy, "• " + fact, 2, BLUE, tracking=1)
        fy += 16
    panel_end = 508

    # three-column band
    cv.hline(left, 518, width, INK, 2)
    colw = 304
    xs = [left, left + 324, left + 648]
    for vx in (left + 314, left + 638):
        cv.vline(vx, 528, 404, GREY, 1)

    # column 1: Shenzhen summit, then COP31
    x = xs[0]
    y = kicker(cv, x, 528, "POLITICS - SHENZHEN")
    y = headline(cv, x, y + 2, ["TRUMP, XI, PUTIN", "SIGN PEACE",
                                "DECLARATION"], scale=3, line_height=23)
    y = draw_wrapped(cv, x, y + 5, SUMMIT_BODY, colw, 2, INK, 17)
    cv.hline(x, y + 10, colw, GREY, 1)
    y = kicker(cv, x, y + 20, "CLIMATE - ANTALYA")
    y = headline(cv, x, y + 2, ["COP31 DRAFT DROPS",
                                "FOSSIL PHASE-OUT"], scale=3,
                 line_height=23)
    draw_wrapped(cv, x, y + 5, COP_BODY, colw, 2, INK, 17)

    # column 2: Anthropic and the sell-off, then Riyadh
    x = xs[1]
    y = kicker(cv, x, 528, "MARKETS - NEW YORK")
    y = headline(cv, x, y + 2, ["ANTHROPIC SOARS ON",
                                "NASDAQ DEBUT"], scale=3, line_height=23)
    y = draw_wrapped(cv, x, y + 5, MARKETS_BODY, colw, 2, INK, 17)
    y += 8
    draw_text(cv, x, y, "MARKET MOVES", 2, GREY, bold=True, tracking=2)
    y += 18
    for name, pct, label in MARKET_MOVES:
        draw_text(cv, x, y, name, 2, INK, tracking=1)
        bw = int(abs(pct) * 5.9)
        col = GREEN if pct > 0 else RED
        cv.rect(x + 118, y + 2, bw, 9, col)
        draw_text(cv, x + 124 + bw, y, label, 2, col, tracking=1)
        y += 16
    cv.hline(x, y + 6, colw, GREY, 1)
    y = kicker(cv, x, y + 12, "MIDDLE EAST - RIYADH")
    y = headline(cv, x, y + 2, ["HOUTHI MISSILE",
                                "HITS RIYADH TOWER"], scale=3,
                 line_height=22)
    draw_wrapped(cv, x, y + 5, HOUTHI_BODY, colw, 2, INK, 17)

    # column 3: Kyiv
    x = xs[2]
    y = kicker(cv, x, 528, "CONFLICT - KYIV")
    y = headline(cv, x, y + 2, ["FRESH MISSILE", "BARRAGE HITS",
                                "KYIV"], scale=3, line_height=23)
    draw_wrapped(cv, x, y + 5, KYIV_BODY, colw, 2, INK, 17)

    # briefs band
    cv.hline(left, 934, width, INK, 2)
    draw_text(cv, left, 942, "AROUND THE WORLD IN BRIEF", 2, RED,
              bold=True, tracking=2)
    src = "SOURCES: IMD - BBC - UN NEWS - AL JAZEERA - NASA"
    draw_text(cv, right - text_width(src, 2, 1), 942, src, 2, GREY,
              tracking=1)
    by = 960
    for brief in BRIEFS:
        draw_text(cv, left, by, brief, 2, INK, tracking=1)
        by += 15
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    save_png(draw_front_page(), os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
