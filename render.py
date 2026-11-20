#!/usr/bin/env python3
"""Render the round-3 front page for make.fun's news-image-20261120 bounty.

Draws a dense broadsheet front page for Friday 20 November 2026 with
Pillow and real TTF fonts: a masthead naming the day, a lead story,
a markets strip, and region sections carrying the day's verified news
(38 stories, 7 regions). The result is written to frontpage.png next
to this file; main.py then copies that asset to the output entry.

The page is drawn at 2x and downscaled with LANCZOS so the type is
smooth. Everything is deterministic: same input, same bytes.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- setup

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "frontpage.png")

S = 2                      # supersample factor
W, H = 1024, 1024          # final size
PAPER = (247, 243, 234)
INK = (18, 20, 24)
GRAY = (96, 98, 102)
FAINT = (203, 197, 182)
BAND = (233, 227, 211)
WHITE = (255, 255, 255)

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-%s.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-%s.ttf"
DEJA_SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"


def font(path_fmt, style, size):
    path = path_fmt % style if "%s" in path_fmt else path_fmt
    return ImageFont.truetype(path, int(size * S))


def serif(size, bold=True):
    return font(SERIF, "Bold" if bold else "Regular", size)


def sans(size, bold=False):
    return font(SANS, "Bold" if bold else "Regular", size)


img = Image.new("RGB", (W * S, H * S), PAPER)
dr = ImageDraw.Draw(img)


def X(v):
    return v * S


def text(x, y, s, fnt, fill=INK, anchor="la"):
    dr.text((X(x), X(y)), s, font=fnt, fill=fill, anchor=anchor)


def line(x0, y0, x1, y1, fill=INK, w=1):
    dr.line([X(x0), X(y0), X(x1), X(y1)], fill=fill, width=max(1, int(w * S)))


def rect(x0, y0, x1, y1, fill=None, outline=None, w=1):
    dr.rectangle([X(x0), X(y0), X(x1), X(y1)], fill=fill,
                 outline=outline, width=max(1, int(w * S)))


def tw(s, fnt):
    return dr.textlength(s, font=fnt) / S


def wrap(s, fnt, maxw):
    """Greedy word wrap; returns a list of lines that fit maxw."""
    words, lines, cur = s.split(), [], ""
    for wd in words:
        trial = wd if not cur else cur + " " + wd
        if tw(trial, fnt) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def ellipsize(s, fnt, maxw):
    if tw(s, fnt) <= maxw:
        return s
    while s and tw(s + "...", fnt) > maxw:
        s = s.rsplit(" ", 1)[0] if " " in s else s[:-1]
    return s + "..." if s else s


# ---------------------------------------------------------------- content
# Every story below was reported on Friday 20 November 2026. Headlines
# carry the key fact; the line under each adds one more verified fact.

LEAD = {
    "kick": "INTERNATIONAL JUSTICE - THE HAGUE",
    "head": "World Court Rules Myanmar Committed Genocide Against the Rohingya",
    "body": ("The International Court of Justice voted 9-6 to hold Myanmar "
             "responsible for genocide - the first time the court has held "
             "a state responsible. The Gambia brought the case over the "
             "2017 military crackdown; more than 1.3 million Rohingya "
             "remain displaced."),
    "src": "BBC / UN NEWS",
}

LEAD_SIDE = [
    {
        "kick": "POLITICS - SHENZHEN",
        "head": "Trump, Xi and Putin Hold First Three-Way Summit in Shenzhen",
        "body": ("The three leaders signed a four-point peace declaration "
                 "on nuclear risk, UN reform and energy. Europe and "
                 "Ukraine were not at the table."),
        "src": "BBC / GUARDIAN",
    },
    {
        "kick": "WEATHER - GOPALPUR, INDIA",
        "head": "Cyclone Akvan Makes Landfall on India's Odisha Coast",
        "body": ("The storm crossed near Gopalpur around noon; more than "
                 "105,000 people had been moved to shelters ahead of it."),
        "src": "IMD / THE HINDU",
    },
]

MARKETS = [
    ("ANTHROPIC +17%", "Record $81.3B Nasdaq debut: closes near $97 vs the $83 offer price"),
    ("AI SELL-OFF", "S&P 500 -2.0%, a fifth straight fall; Nikkei -4.8%, SoftBank -16%"),
    ("GOLD -4.2%", "A strong dollar and a US 10-year yield above 5% weigh on bullion"),
    ("BRENT $90.05", "Oil +0.7% as Hormuz tanker attacks keep supply fears high"),
]

# (region, [(headline, one factual line, source), ...])
REGIONS = [
    ("EUROPE", [
        ("Russian Strikes Hit Kyiv's Bridges, Killing Eight",
         "28 injured in attacks across nine regions of Ukraine", "BBC"),
        ("Ukraine Hits Crimea Bridge for Third Time in Four Days",
         "Rail traffic halted; Putin vows a painful reply", "BBC"),
        ("Allies in Berlin: No Ukraine Deal Without Europe at the Table",
         "Merz rejects great-power carve-up of Ukraine's future", "FRANCE 24"),
        ("UK and EU Clinch Youth Mobility and Food Trade Deals",
         "100,000 young people a year could work across the Channel", "BBC"),
        ("Young Europeans Strike Over Living Costs and Rearmament",
         "Protests in 25+ countries; 300+ schools walk out", "STRAITS TIMES"),
    ]),
    ("ASIA-PACIFIC", [
        ("IAEA: North Korea Expanding Uranium Enrichment at Yongbyon",
         "Inspectors barred from the site since 2009", "EURONEWS"),
        ("Japan Inflation Hits Year's High as Subsidies Expire",
         "Core prices just under forecast; yen near 159", "JAPAN TIMES"),
        ("Pakistan Says 22 Militants Killed in Border Raids",
         "Hideouts hit in Khyber Pakhtunkhwa province", "THE HINDU"),
        ("Bangladesh Violence Flares Ahead of Hasina's Return",
         "Arson in Gopalganj; her passport plea rejected", "THE GUARDIAN"),
        ("India's IFFI Film Festival Opens in Goa",
         "The country's flagship cinema showcase opens", "THE HINDU"),
    ]),
    ("MIDDLE EAST", [
        ("Houthi Missiles Damage Riyadh's PIF Tower",
         "Financial district hit; no injuries, Gulf states condemn", "SKY NEWS"),
        ("Iran War Enters Ninth Month; Tankers Hit in Hormuz",
         "Tanker ablaze after hitting a mine; US cost $48.3B", "JAPAN TIMES"),
        ("Israeli Troops Cross Gaza's Yellow Line, First Since Truce",
         "Tunnel raid in Gaza; Hamas cries ceasefire violation", "BBC"),
        ("COP31 Draft Drops Call to Phase Out Fossil Fuels",
         "Dropped on the final day; Pacific states object", "JAPAN TIMES"),
    ]),
    ("AFRICA", [
        ("Dozens Missing as Migrant Boat Capsizes Off Senegal",
         "Boat of 50-100 sank off Yenne; four bodies found", "BBC"),
        ("Drone Strike Kills 10 at a Sudan Gold Mine",
         "Bajoun mine hit amid the army-RSF war", "ALLAFRICA"),
        ("US Consortium Wins Kenya's Mrima Hill Minerals Deal",
         "An estimated $60B in critical-mineral deposits", "BBC"),
        ("Zimbabwe Destroys Its 250,000th Landmine",
         "HALO Trust milestone; 2030 goal at risk", "AFRICANEWS"),
    ]),
    ("NORTH AMERICA", [
        ("California Probes Nvidia After CEO Huang Resigns",
         "Subpoena asks if chips or data reached China", "CNBC"),
        ("White House Fires Cyber Director After Week of Outages",
         "Out after failures hit flights and email systems", "FRANCE 24"),
        ("Senate Passes Energy Permitting Overhaul, 62-33",
         "Faster power and grid approvals; House votes next", "CNBC"),
        ("Houston Rout Indianapolis 26-3 in the NFL",
         "Rams receiver Puka Nacua suspended three games", "AP"),
    ]),
    ("SOUTH AMERICA", [
        ("Brazil Sells $1 Billion From Reserves to Curb the Dollar",
         "Real down 18% in a month, near 5.93 per dollar", "MERCOPRESS"),
        ("US and Venezuela Sign Military Cooperation Deal",
         "Hegseth signs in Caracas after Maduro's removal", "BBC"),
        ("El Nino Rains Affect 93,000 People Across Ecuador",
         "25,600 homes damaged across all 24 provinces", "UN OCHA"),
    ]),
    ("OCEANIA", [
        ("Nicholls' 146* Lifts New Zealand to 317-6 in Wellington",
         "Day two: hosts build a strong first-innings total", "NZ HERALD"),
    ]),
    ("SCIENCE & SPACE", [
        ("Voyager 1 Reaches One Light-Day From Earth",
         "Its signal now takes a full day to reach Earth", "NASA"),
    ]),
]

TICKER = [
    "Poland: Russian missiles and a drone violated our airspace overnight",
    "Estonia closes its Russian border for six months; Moscow cries 'Iron Curtain'",
    "GTA VI launch tops $2.3B, set to be the biggest entertainment launch ever",
    "Fiji and Tonga declare drought disasters as El Nino bites the Pacific",
]

N_STORIES = (1 + len(LEAD_SIDE) + len(MARKETS)
             + sum(len(st) for _, st in REGIONS) + len(TICKER))

# ---------------------------------------------------------------- masthead

M = 16                      # page margin
CW = W - 2 * M              # content width

text(M, 10, "THE GLOBAL FRONT PAGE - ONE IMAGE, THE WHOLE DAY",
     sans(9, True), GRAY)
text(W - M, 10, "VOL. I - NO. 321", sans(9, True), GRAY, anchor="ra")

f_mast = ImageFont.truetype(DEJA_SERIF_B, int(57 * S))
text(W / 2, 24, "THE WORLD TODAY", f_mast, INK, anchor="ma")

line(M, 90, W - M, 90, INK, 3)
line(M, 95, W - M, 95, INK, 1)

rect(M, 100, W - M, 132, fill=INK)
text(M + 12, 107, "FRIDAY 20 NOVEMBER 2026", sans(17, True), WHITE)
text(W - M - 12, 109, "%d STORIES - 7 REGIONS - ONE DAY" % N_STORIES,
     sans(13, True), WHITE, anchor="ra")

# ---------------------------------------------------------------- lead row

LY = 144
line(M, LY + 186, W - M, LY + 186, INK, 1)

# lead story, left
lw = 492
text(M, LY, LEAD["kick"], sans(10, True), GRAY)
lines = wrap(LEAD["head"], serif(26), lw)
yy = LY + 16
for ln in lines:
    text(M, yy, ln, serif(26))
    yy += 31
yy += 2
for ln in wrap(LEAD["body"], sans(11.5), lw):
    text(M, yy, ln, sans(11.5))
    yy += 15.5
text(M, yy + 3, "SOURCES: " + LEAD["src"], sans(8.5, True), GRAY)

# vertical divider
line(M + lw + 14, LY + 2, M + lw + 14, LY + 182, FAINT, 1)

# two side stories, right
sx = M + lw + 28
sw = W - M - sx
sy = LY
for i, st in enumerate(LEAD_SIDE):
    text(sx, sy, st["kick"], sans(9.5, True), GRAY)
    yy = sy + 14
    for ln in wrap(st["head"], serif(16.5), sw):
        text(sx, yy, ln, serif(16.5))
        yy += 20
    yy += 1
    for ln in wrap(st["body"], sans(10.5), sw):
        text(sx, yy, ln, sans(10.5))
        yy += 14
    text(sx, yy + 2, "SOURCES: " + st["src"], sans(8, True), GRAY)
    sy = yy + 16
    if i == 0:
        line(sx, sy - 6, W - M, sy - 6, FAINT, 1)

# tiny cyclone spiral beside the Akvan block: it sits right of the
# body's second line and the sources line, in the clear band between
# the first body line (ends y=286) and the lead-row rule (y=330), so
# no glyph ever touches the graphic
cx, cy, r0 = W - M - 36, LY + 163, 17
for k in range(3):
    a0 = k * 2.1
    pts = []
    for t in range(0, 44):
        ang = a0 + t * 0.16
        r = r0 * (0.25 + 0.75 * t / 44.0)
        pts.append((X(cx + r * math.cos(ang)), X(cy + r * math.sin(ang))))
    dr.line(pts, fill=GRAY, width=int(1.6 * S))
dr.ellipse([X(cx - 3), X(cy - 3), X(cx + 3), X(cy + 3)], fill=GRAY)

# ---------------------------------------------------------------- markets

MY = LY + 194
rect(M, MY, W - M, MY + 46, fill=BAND)
text(M + 10, MY + 5, "MARKETS", sans(9, True), GRAY)
cellw = CW / 4.0
for i, (big, small) in enumerate(MARKETS):
    x0 = M + i * cellw
    if i:
        line(x0, MY + 6, x0, MY + 40, FAINT, 1)
    text(x0 + 10, MY + 13, big, serif(14.5))
    sml = wrap(small, sans(8.5), cellw - 18)[:2]
    yy = MY + 31
    for ln in sml:
        text(x0 + 10, yy, ln, sans(8.5), GRAY)
        yy += 10.5

# ---------------------------------------------------------------- columns

TOP = MY + 58
BOT = 952
COLW = 322
GUT = 13
COLX = [M, M + COLW + GUT, M + 2 * (COLW + GUT)]

F_RH = sans(12.5, True)      # region header
F_H = serif(13)              # story headline
F_B = sans(10.5)             # story body line
RH_H = 22                    # region header height
H_LH, B_LH = 16, 13.5        # line heights


def story_h(head, body):
    nh = len(wrap(head, F_H, COLW - 4))
    return nh * H_LH + B_LH + 8


def region_h(stories):
    return RH_H + 5 + sum(story_h(h, b) for h, b, _ in stories) + 4


# greedy: put each region block into the currently shortest column
cols = [[], [], []]
heights = [0, 0, 0]
for name, stories in REGIONS:
    h = region_h(stories)
    c = heights.index(min(heights))
    cols[c].append((name, stories))
    heights[c] += h + 8

print("column heights:", heights, "budget:", BOT - TOP)


def draw_region(x, y, name, stories):
    rect(x, y, x + COLW, y + RH_H, fill=INK)
    text(x + 8, y + 4, name, F_RH, WHITE)
    y += RH_H + 5
    for head, body, src in stories:
        for ln in wrap(head, F_H, COLW - 4):
            text(x, y, ln, F_H)
            y += H_LH
        tag = " - " + src
        if tw(body, F_B) + tw(tag, F_B) <= COLW - 4:
            text(x, y, body, F_B)
            text(x + tw(body, F_B) + 3, y, tag, F_B, GRAY)
        else:
            text(x, y, ellipsize(body, F_B, COLW - 4), F_B)
        y += B_LH + 8
        line(x, y - 4, x + COLW, y - 4, FAINT, 1)
    return y


for c in range(3):
    y = TOP
    for name, stories in cols[c]:
        y = draw_region(COLX[c], y, name, stories) + 8

# ---------------------------------------------------------------- ticker

line(M, 958, W - M, 958, INK, 2)
f_tk = sans(9.5)
text(M, 965, "IN BRIEF", sans(10, True))
tx = M + tw("IN BRIEF", sans(10, True)) + 10
tick = "   -   ".join(TICKER)
# wrap the ticker manually: first line starts at tx, rest full width
words, lines, cur, maxw = tick.split(), [], "", CW - (tx - M)
for wd in words:
    trial = wd if not cur else cur + " " + wd
    if tw(trial, f_tk) <= maxw or not cur:
        cur = trial
    else:
        lines.append(cur)
        cur = wd
        maxw = CW
if cur:
    lines.append(cur)
yy = 965
for i, ln in enumerate(lines[:2]):
    text(tx if i == 0 else M, yy, ln, f_tk)
    yy += 13

line(M, 1000, W - M, 1000, FAINT, 1)
text(W / 2, 1004,
     "Compiled from the day's wire and newsroom reports - BBC, AP, Al Jazeera, "
     "France 24, The Hindu, Japan Times, CNBC, RNZ, NASA and others",
     sans(8), GRAY, anchor="ma")

# ---------------------------------------------------------------- finish

img = img.resize((W, H), Image.LANCZOS)
img.save(OUT)
print("wrote", OUT, os.path.getsize(OUT), "bytes;", N_STORIES, "stories")
