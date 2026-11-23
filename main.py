#!/usr/bin/env python3
"""The World in One Day -- Monday 23 November 2026.

A single 1024x1024 front page summing up the day's world news.
Draws everything with PIL primitives: no network, no external images,
no randomness, no clock. Fonts are bundled in fonts/ next to this file,
so the program does not depend on system fonts.

Layout (1024 x 1024, cream newsprint):
  masthead -> 3 hero stories -> 10 numbered features (2 x 5)
  -> world map "WHERE IT HAPPENED" with 13 numbered pins + key
  -> 19 one-line briefs in two columns -> source footer
Total: 3 + 10 + 13 + 19 = 45 stories.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("ENTRY_OUT", "/output/entry.png")

# ---------------------------------------------------------------- palette
CREAM = (248, 241, 220)
PAPER = (252, 247, 232)
INK = (34, 48, 74)
INK_SOFT = (74, 82, 96)
MUTED = (110, 108, 96)
RULE = (34, 48, 74)
RED = (196, 80, 60)        # conflict
BLUE = (62, 107, 140)      # politics
GREEN = (94, 140, 97)      # climate
AMBER = (192, 138, 45)     # markets / disaster
PURPLE = (122, 92, 140)    # culture / sport
TEAL = (78, 138, 138)
SEA = (220, 233, 238)
LAND = (201, 214, 184)
SAND = (242, 216, 167)
ROSE = (232, 201, 192)
SAGE = (213, 227, 200)
LAV = (227, 214, 238)
GOLD = (233, 181, 76)


def F(name, size):
    return ImageFont.truetype(os.path.join(BASE, "fonts", name), size)


SERIF_B = lambda s: F("DejaVuSerif-Bold.ttf", s)
SERIF = lambda s: F("DejaVuSerif.ttf", s)
SANS_B = lambda s: F("DejaVuSans-Bold.ttf", s)
SANS = lambda s: F("DejaVuSans.ttf", s)


def wrap(text, font, max_w, draw):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def para(d, x, y, text, font, fill, max_w, leading, max_lines=None):
    lines = wrap(text, font, max_w, d)
    if max_lines:
        lines = lines[:max_lines]
    for ln in lines:
        d.text((x, y), ln, font=font, fill=fill)
        y += leading
    return y


def rule(d, x0, y, x1, w=2, fill=RULE):
    d.line([(x0, y), (x1, y)], fill=fill, width=w)


def num_badge(d, cx, cy, n, fill, r=11):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)
    f = SANS_B(13)
    t = str(n)
    d.text((cx - d.textlength(t, font=f) / 2, cy - 8), t, font=f, fill=(255, 255, 255))


# ---------------------------------------------------------------- heroes
HEROES = [
    {
        "kicker": "CLIMATE  ·  ANTALYA",
        "color": GREEN,
        "sky": SAND,
        "headline": "COP31 COLLAPSES IN ANTALYA",
        "dek": "Two days overtime, no deal. The longest climate summit ever ends in deadlock over fossil fuels.",
        "art": "cop31",
    },
    {
        "kicker": "UKRAINE  ·  BENGHAZI",
        "color": RED,
        "sky": (191, 220, 232),
        "headline": "UKRAINE SINKS RUSSIAN WARSHIP IN LIBYA",
        "dek": "Seven sea drones sink the corvette Merkury at Benghazi, 1,500 miles from the front line.",
        "art": "benghazi",
    },
    {
        "kicker": "IRAN WAR  ·  HORMUZ",
        "color": RED,
        "sky": (191, 220, 232),
        "headline": "TANKERS ATTACKED IN THE STRAIT OF HORMUZ",
        "dek": "Iran strikes hit ships and Bahrain as Trump says Tehran wants a deal — “not an acceptable one”.",
        "art": "hormuz",
    },
]


def art_cop31(d, x, y, w, h):
    # amber sun, cracked globe, three small flags
    d.ellipse([x + w - 78, y + 10, x + w - 18, y + 70], fill=GOLD)
    d.ellipse([x + w - 66, y + 22, x + w - 30, y + 58], fill=(247, 214, 130))
    cx, cy, r = x + w // 2 - 20, y + h - 52, 44
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(139, 178, 140))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(90, 120, 90), width=2)
    d.arc([cx - r, cy - r, cx + r, cy + r], 200, 340, fill=(90, 120, 90), width=2)
    d.line([(cx - r + 8, cy - 18), (cx - 6, cy + 2), (cx + 10, cy - 8),
            (cx + 22, cy + 16), (cx + r - 6, cy + 4)], fill=(70, 60, 50), width=3)
    for i, c in enumerate((RED, BLUE, GREEN)):
        fx = x + 16 + i * 26
        d.line([(fx, y + h - 26), (fx, y + h - 6)], fill=INK, width=2)
        d.polygon([(fx, y + h - 26), (fx + 18, y + h - 21), (fx, y + h - 16)],
                  fill=c)


def art_benghazi(d, x, y, w, h):
    # sea, warship hull, explosion starburst, two drones
    d.rectangle([x, y + h - 46, x + w, y + h], fill=(120, 165, 190))
    for i in range(3):
        wx = x + 14 + i * 90
        d.arc([wx, y + h - 52, wx + 60, y + h - 34], 180, 360,
              fill=(235, 244, 248), width=2)
    # explosion
    ex, ey = x + w // 2 + 30, y + 42
    pts = []
    import math
    for i in range(16):
        ang = i * math.pi / 8
        rr = 34 if i % 2 == 0 else 16
        pts.append((ex + rr * math.cos(ang), ey + rr * math.sin(ang)))
    d.polygon(pts, fill=(233, 150, 60))
    d.polygon([(ex - 12, ey - 6), (ex + 12, ey - 6), (ex, ey + 12)],
              fill=(247, 214, 110))
    # hull
    d.polygon([(x + 30, y + h - 58), (x + w - 24, y + h - 58),
               (x + w - 52, y + h - 34), (x + 58, y + h - 34)], fill=INK)
    d.rectangle([x + 120, y + h - 86, x + 170, y + h - 58], fill=INK)
    d.line([(x + 145, y + h - 108), (x + 145, y + h - 86)], fill=INK, width=3)
    d.polygon([(x + 145, y + h - 108), (x + 168, y + h - 100),
               (x + 145, y + h - 94)], fill=RED)
    # drones
    for dx, dy in ((x + 44, y + 30), (x + 92, y + 18)):
        d.ellipse([dx - 5, dy - 5, dx + 5, dy + 5], fill=(60, 60, 60))
        d.line([(dx, dy + 6), (dx + 26, dy + 22)], fill=(60, 60, 60), width=1)


def art_hormuz(d, x, y, w, h):
    # sandy banks, blue channel, tanker, flames
    d.polygon([(x, y), (x + w, y), (x + w, y + 34), (x, y + 52)], fill=(226, 198, 150))
    d.polygon([(x, y + h), (x + w, y + h), (x + w, y + h - 30), (x, y + h - 48)],
              fill=(226, 198, 150))
    d.polygon([(x, y + 44), (x + w, y + 26), (x + w, y + h - 38),
               (x, y + h - 40)], fill=(96, 150, 180))
    # tanker
    tx, ty = x + 52, y + h // 2 - 8
    d.rectangle([tx, ty, tx + 190, ty + 30], fill=(140, 52, 44))
    for i, c in enumerate(((240, 240, 235), (247, 214, 110), (139, 178, 140))):
        d.rectangle([tx + 12 + i * 30, ty - 12, tx + 36 + i * 30, ty],
                    fill=c, outline=INK, width=1)
    d.rectangle([tx + 190, ty - 18, tx + 214, ty + 30], fill=(90, 40, 36))
    # flames
    for fx in (tx + 60, tx + 150):
        d.polygon([(fx - 12, ty), (fx, ty - 26), (fx + 12, ty)], fill=(233, 150, 60))
        d.polygon([(fx - 6, ty), (fx, ty - 14), (fx + 6, ty)], fill=(247, 214, 110))
    # waves
    for i in range(4):
        wx = x + 16 + i * 74
        d.arc([wx, y + h - 24, wx + 44, y + h - 10], 180, 360,
              fill=(235, 244, 248), width=2)


ART = {"cop31": art_cop31, "benghazi": art_benghazi, "hormuz": art_hormuz}

# ---------------------------------------------------------------- features
FEATURES = [
    (4, "NATO EMERGENCY TALKS", "Three Russian missiles land in Poland; allies meet in Brussels.", BLUE),
    (5, "DYMER: 11 DEAD", "Strike on Kyiv-region flats; a 79-year-old is pulled alive.", RED),
    (6, "DEMOCRATS WIN 258 SEATS", "Largest House majority in decades; Trump moves to curb oversight.", BLUE),
    (7, "AI ROUT HITS MARKETS", "Nikkei −5.1%, S&P −3.7%; gold jumps 3.1% as fear spreads.", AMBER),
    (8, "ICJ: MYANMAR GUILTY OF GENOCIDE", "First such ruling, for the Rohingya people.", BLUE),
    (9, "GAZA: 3 KILLED IN TRUCK STRIKE", "Oxfam: toxic contamination covers 99% of Gaza.", RED),
    (10, "EISENKOT: SETTLER ARSON IS “JEWISH TERRORISM”", "PM-elect condemns attacks on West Bank villages.", RED),
    (11, "NVIDIA CHIEF QUITS", "Huang resigns; Trump urges rehire; shares jump 7%.", TEAL),
    (12, "PROOF CLAIMED FOR RIEMANN", "Anthropic mathematician and Claude say the 160-year puzzle is solved.", PURPLE),
    (13, "ALCARAZ WINS ATP FINALS", "Beats Zverev 6–2, 7–6 for a maiden title in Turin.", PURPLE),
]

# ---------------------------------------------------------------- map pins
# (number, label, lon, lat, color, display offset dx, dy)
PINS = [
    (14, "ANTALYA — COP31 ends with no climate deal", 30.7, 36.9, GREEN, -2, 24),
    (15, "BENGHAZI — Ukraine sinks Russian corvette Merkury", 20.1, 32.1, RED, -26, 0),
    (16, "HORMUZ — Three tankers attacked", 56.5, 26.5, RED, 0, -14),
    (17, "BAHRAIN — IRGC strikes hit industrial site", 50.6, 26.2, RED, 16, 8),
    (18, "DYMER — Strike kills 11 in Kyiv region", 30.3, 50.8, RED, -24, -12),
    (19, "KRYVYI RIH — Child killed in overnight attack", 33.4, 47.9, RED, 0, 0),
    (20, "KHARKIV — Drone hits a kindergarten", 36.2, 50.0, RED, 24, -10),
    (21, "GAZA — Truck strike kills three", 34.5, 31.5, RED, -24, 10),
    (22, "RAMALLAH — Settler arson condemned", 35.2, 31.9, RED, 24, 12),
    (23, "BRUSSELS — NATO meets on Poland missiles", 4.4, 50.9, BLUE, 0, 0),
    (24, "KHARTOUM — Drones hit a UN building", 32.5, 15.6, RED, -20, 14),
    (25, "INDONESIA — Factory fire kills three", 106.8, -6.2, AMBER, 0, 0),
    (26, "S. SUDAN — Attack kills 24 civilians", 31.6, 7.9, RED, 14, 6),
]

CONTINENTS = {
    "NA": [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-75, 73), (-55, 60),
           (-60, 47), (-75, 35), (-80, 25), (-90, 20), (-97, 16), (-105, 20),
           (-115, 28), (-125, 40), (-150, 60)],
    "SA": [(-80, 10), (-60, 8), (-50, 0), (-40, -10), (-50, -25), (-60, -35),
           (-70, -50), (-75, -35), (-80, -20), (-80, 0)],
    "AF": [(-17, 15), (-10, 30), (10, 37), (30, 31), (35, 28), (43, 12),
           (51, 10), (40, -5), (35, -20), (20, -35), (12, -18), (8, 4), (-8, 5)],
    "EU": [(-10, 36), (-2, 48), (5, 58), (10, 60), (20, 70), (30, 70),
           (40, 60), (30, 45), (20, 40), (10, 38), (0, 36)],
    "AS": [(40, 70), (60, 73), (90, 75), (120, 73), (150, 70), (170, 66),
           (160, 60), (140, 40), (130, 35), (120, 25), (105, 10), (100, 8),
           (90, 15), (80, 8), (70, 20), (60, 25), (50, 30), (43, 40)],
    "OC": [(113, -22), (130, -12), (142, -11), (150, -22), (153, -27),
           (147, -38), (140, -38), (129, -32), (114, -30)],
}

# ---------------------------------------------------------------- briefs
BRIEFS = [
    (27, "S. KOREA EXAM CHIEF RESIGNS OVER AI CHEATING"),
    (28, "CHINA WARNS CITIZENS OFF MT. FUJI"),
    (29, "DENMARK: RUSSIA PLOTTED TO KILL RAPPER IN COPENHAGEN"),
    (30, "BELGRADE FLOODS AFTER RECORD RAIN"),
    (31, "“CHAPO ISIDRO” CAPTURED IN MEXICO"),
    (32, "BANGLADESH: HASINA TO BE JAILED IF SHE RETURNS"),
    (33, "OREGON, VIRGINIA SUE SPACEX OVER AI CLAIMS"),
    (34, "TAIWAN STOCKS PLUNGE; SHORT-SELLING CURBED"),
    (35, "INDIA 720/9 IN WELLINGTON TEST"),
    (36, "PAKISTAN A BEAT INDIA A BY 48 RUNS"),
    (37, "MÁRQUEZ EQUALS AGOSTINI’S 8TH MOTOGP TITLE"),
    (38, "BOCA JUNIORS WIN COPA SUDAMERICANA"),
    (39, "PRICE WINS GRAND SLAM OF DARTS"),
    (40, "INDIA–CHINA BORDER TALKS IN ARUNACHAL"),
    (41, "MODI: AI CANNOT REPLACE SKILLED WORKERS"),
    (42, "EPSTEIN RUSSIA LINKS CHALLENGE SUICIDE RULING"),
    (43, "TRUMP, PUTIN, XI SIGN SHENZHEN PEACE DECLARATION"),
    (44, "ISTANBUL MARCHES OVER SÖZCÜ TV SEIZURE"),
    (45, "US AVIATION CHAOS FUELS ATC FUNDING FIGHT"),
]


def project(lon, lat, mx, my, mw, mh):
    px = mx + (lon + 170.0) / 360.0 * mw
    py = my + (75.0 - lat) / 130.0 * mh
    return px, py


def main():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    X0, X1 = 22, 1002

    # ---------------------------------------------------------- masthead
    rule(d, X0, 16, X1, 3)
    d.text((W // 2 - d.textlength("THE DAY IN WORLD NEWS", font=SERIF_B(56)) / 2,
            24), "THE DAY IN WORLD NEWS", font=SERIF_B(56), fill=INK)
    d.text((X0, 88), "MONDAY 23 NOVEMBER 2026", font=SANS_B(15), fill=INK)
    right = "45 STORIES  ·  6 CONTINENTS  ·  ONE DAY"
    d.text((X1 - d.textlength(right, font=SANS_B(15)), 88), right,
           font=SANS_B(15), fill=INK)
    rule(d, X0, 108, X1, 2)

    # ---------------------------------------------------------- heroes
    hy, hh = 118, 268
    cw = (X1 - X0 - 20) // 3
    for i, hero in enumerate(HEROES):
        x = X0 + i * (cw + 10)
        d.rounded_rectangle([x, hy, x + cw, hy + 148], radius=6,
                            fill=hero["sky"], outline=(200, 190, 160), width=1)
        ART[hero["art"]](d, x, hy, cw, 148)
        d.text((x, hy + 156), hero["kicker"], font=SANS_B(10),
               fill=hero["color"])
        y = para(d, x, hy + 172, hero["headline"], SERIF_B(18), INK, cw, 21,
                 max_lines=3)
        para(d, x, y + 2, hero["dek"], SANS(11), INK_SOFT, cw, 14, max_lines=3)
    rule(d, X0, 396, X1, 1, fill=(170, 160, 130))

    # ---------------------------------------------------------- features
    fy = 406
    d.text((W // 2 - d.textlength("TEN MORE THAT MATTER", font=SANS_B(13)) / 2,
            fy), "TEN MORE THAT MATTER", font=SANS_B(13), fill=MUTED)
    gy = 428
    gw = (X1 - X0 - 32) // 5
    gh = 96
    for i, (n, head, dek, color) in enumerate(FEATURES):
        col, row = i % 5, i // 5
        x = X0 + col * (gw + 8)
        y = gy + row * (gh + 6)
        num_badge(d, x + 11, y + 11, n, color)
        tx = x + 28
        y2 = para(d, tx, y, head, SANS_B(12), INK, gw - 28, 15, max_lines=3)
        para(d, tx, y2 + 1, dek, SANS(10), INK_SOFT, gw - 28, 13, max_lines=3)
        if col < 4:
            d.line([(x + gw + 3, y + 4), (x + gw + 3, y + gh - 6)],
                   fill=(210, 200, 170), width=1)
    rule(d, X0, 634, X1, 1, fill=(170, 160, 130))

    # ---------------------------------------------------------- map
    my = 642
    d.text((X0, my), "WHERE IT HAPPENED", font=SERIF_B(20), fill=INK)
    legend = [(RED, "CONFLICT"), (BLUE, "POLITICS"), (GREEN, "CLIMATE"),
              (AMBER, "MARKETS")]
    lx = X1
    for color, name in reversed(legend):
        tw = d.textlength(name, font=SANS_B(9))
        lx -= tw + 22
        d.ellipse([lx, my + 6, lx + 10, my + 16], fill=color)
        d.text((lx + 13, my + 5), name, font=SANS_B(9), fill=INK_SOFT)
        lx -= 10
    mx, mw, mh = X0, 600, 170
    mapy = my + 26
    d.rounded_rectangle([mx, mapy, mx + mw, mapy + mh], radius=6, fill=SEA,
                        outline=(190, 200, 200), width=1)
    for pts in CONTINENTS.values():
        d.polygon([project(lon, lat, mx, mapy, mw, mh) for lon, lat in pts],
                  fill=LAND, outline=(150, 165, 130))
    d.text((mx + 10, mapy + mh - 20), "WORLD MAP — PINS 14–26",
           font=SANS_B(9), fill=(90, 110, 120))
    for n, _label, lon, lat, color, dx, dy in PINS:
        px, py = project(lon, lat, mx, mapy, mw, mh)
        qx, qy = px + dx, py + dy
        if dx or dy:
            d.line([(px, py), (qx, qy)], fill=(120, 120, 110), width=1)
            d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(120, 120, 110))
        d.ellipse([qx - 8, qy - 8, qx + 8, qy + 8], fill=color,
                  outline=(255, 255, 255), width=2)
        f = SANS_B(9)
        t = str(n)
        d.text((qx - d.textlength(t, font=f) / 2, qy - 6), t, font=f,
               fill=(255, 255, 255))
    # key list beside the map
    kx = mx + mw + 14
    kw = X1 - kx
    d.text((kx, mapy), "THE MAP, IN WORDS", font=SANS_B(11), fill=INK)
    yy = mapy + 18
    for n, label, _lon, _lat, color, _dx, _dy in PINS:
        d.ellipse([kx, yy + 2, kx + 8, yy + 10], fill=color)
        yy = para(d, kx + 13, yy, "%d  %s" % (n, label), SANS(9), INK,
                  kw - 13, 11, max_lines=1) + 1
    rule(d, X0, 846, X1, 1, fill=(170, 160, 130))

    # ---------------------------------------------------------- briefs
    by = 854
    d.text((X0, by), "THE REST OF THE DAY", font=SERIF_B(16), fill=INK)
    d.text((X1 - d.textlength("19 MORE STORIES", font=SANS_B(10)), by + 3),
           "19 MORE STORIES", font=SANS_B(10), fill=MUTED)
    colw = (X1 - X0 - 24) // 2
    left, right = BRIEFS[:10], BRIEFS[10:]
    for ci, col in enumerate((left, right)):
        x = X0 + ci * (colw + 24)
        y = by + 26
        for n, head in col:
            d.text((x, y), "%d" % n, font=SANS_B(11), fill=AMBER)
            d.text((x + 24, y), head, font=SANS(11), fill=INK)
            y += 12
    rule(d, X0, 1004, X1, 2)

    # ---------------------------------------------------------- footer
    d.text((X0, 1010),
           "Sources: AP · Reuters · UN News · Al Jazeera · The Guardian · "
           "Just Security · 23 Nov 2026",
           font=SANS(9), fill=MUTED)
    foot_r = "THE DAY IN WORLD NEWS"
    d.text((X1 - d.textlength(foot_r, font=SANS_B(9)), 1010), foot_r,
           font=SANS_B(9), fill=MUTED)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.save(OUT, format="PNG")
    print("wrote", OUT, img.size)


if __name__ == "__main__":
    main()
