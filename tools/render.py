#!/usr/bin/env python3
"""Render the front page for Friday 20 November 2026 into entry.png.

Deterministic: no network, no clock, no randomness. Every fact on the page
comes from the researched brief for 20 Nov 2026 (see README.md). All text
is measured with the actual font before drawing; every drawn bounding box
is asserted to fit its cell, and the full manifest is returned for audit.

Run:  python3 tools/render.py            # writes entry.png at repo root
      python3 tools/render.py --text     # also dump the page text to stdout
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

W = H = 1024
M = 22                      # side margin
CW = W - 2 * M              # content width = 980

PAPER = (244, 241, 234)     # f4f1ea
INK = (26, 26, 26)          # 1a1a1a
RULE = (216, 211, 198)      # d8d3c6
ACCENT = (179, 36, 31)      # b3241f
SECOND = (47, 72, 88)       # 2f4858

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
FONTS = {
    ("serif", False): "DejaVuSerif.ttf",
    ("serif", True): "DejaVuSerif-Bold.ttf",
    ("sans", False): "DejaVuSans.ttf",
    ("sans", True): "DejaVuSans-Bold.ttf",
}
_font_cache = {}


def font(family, bold, size):
    key = (family, bold, size)
    if key not in _font_cache:
        path = os.path.join(FONT_DIR, FONTS[(family, bold)])
        if not os.path.exists(path):
            raise SystemExit("missing font: " + path)
        _font_cache[key] = ImageFont.truetype(path, size)
    return _font_cache[key]


# ---------------------------------------------------------------- layout data
# tier: hero / medium / brief. Every string below is sourced from the brief.
HEROES = [
    dict(
        field="Conflict",
        headline="Russian missiles hit Kyiv; two fall in Poland",
        summary=("About 12 ballistic missiles and drones hit Kyiv overnight, "
                 "killing at least 3. A Kh-101 fell in a field near Nowy "
                 "Lipowiec; NATO called it a violation."),
        place="Kyiv, Ukraine · Lublin, Poland",
        source="AP",
    ),
    dict(
        field="Science and AI",
        headline="Anthropic mathematician claims Riemann proof",
        summary=("Levent Alpöge says six weeks with Claude yielded a proof of "
                 "the Riemann hypothesis. The Lean version exceeds 250,000 "
                 "lines; Tao says verification is some way off."),
        place="Anthropic · a day after its market debut",
        source="BBC · Nature · AFP",
    ),
    dict(
        field="Climate",
        headline="COP31 closes in Antalya without the words fossil fuels",
        summary=("The closing draft dropped every mention of fossil fuels and "
                 "the $120bn adaptation figure. Protesters held \"Shame\" signs "
                 "at the plenary; the final text was due at midnight."),
        place="Antalya",
        source="AP",
    ),
]

MEDIUM = [
    dict(field="Labour", headline="Italy stops for a 24-hour general strike",
         line="About 100 squares march against the budget", place="Rome · Italy"),
    dict(field="Labour", headline="Portugal's public sector walks out",
         line="Unions seek 15% and a €1,150 minimum wage", place="Portugal"),
    dict(field="Shipping", headline="Tanker ablaze in the Strait of Hormuz",
         line="IRGC and UKMTO report fire off Khasab", place="Khasab, Oman"),
    dict(field="Conflict", headline="Saudi-led coalition strikes Yemen",
         line="Ops kill or injure 193 Houthi fighters", place="Hodeidah · Sanaa · Taiz"),
    dict(field="Security", headline="Iraq agrees joint ops with Kata'ib Hezbollah",
         line="Al-Zaidi: joint centre and troops deployed", place="Jurf al-Sakhar"),
    dict(field="Disaster", headline="30 dead as funeral boat capsizes",
         line="Around 300 missing in Bayelsa State", place="Nigeria"),
    dict(field="Seismic", headline="Magnitude 6.7 quake hits central Peru",
         line="Felt in Lima; no fatalities reported", place="30 km north-west of Junín"),
    dict(field="Rights", headline="UN court finds genocide in Myanmar",
         line="Sanctions urged; China and Russia could veto", place="Myanmar · United Nations"),
    dict(field="Markets", headline="Seventh straight fall for Asia stocks",
         line="Nikkei -4.6%; Kospi below 5,000", place="Tokyo · Seoul"),
    dict(field="Weather", headline="Cyclone Akvan bears down on Odisha",
         line="105,000 evacuated; landfall near Gopalpur", place="Odisha, India"),
    dict(field="Tech policy", headline="Trump threatens tax on AI data centres",
         line="Senate bill speeds permits, charges energy", place="Washington"),
    dict(field="Diplomacy", headline="UK and EU rebuild post-Brexit ties",
         line="Trade and travel deals at a rare summit", place="London · Brussels"),
]

BRIEFS = [
    ("Haiti / El Salvador", "Three prisons agreed for gang members"),
    ("El Salvador", "Three soldiers killed as explosives detonate"),
    ("Alaska", "DOJ moves to drop suit over Peltola's Senate win"),
    ("Malaysia", "Anwar: air-force officers suspected of smuggling drugs"),
    ("France", "De Villepin to run in the 2027 presidential election"),
    ("Wellington", "NZ 317-6 v India: Phillips 118, Nicholls 146 not out"),
    ("Turin", "ATP Finals group stage ends"),
    ("Las Vegas", "Grand Prix washed out"),
    ("Hong Kong", "India beat Malaysia at the Hong Kong Open"),
    ("US", "FBI: sextortion of minors headed for worst year on record"),
    ("Cincinnati", "Fiona the hippo dies after eating a visitor's hat"),
    ("WWE", "Dwayne Johnson announces his return"),
    ("US Capitol", "76-foot Engelmann spruce arrives after 2,000 miles"),
    ("Interpol", "Carback II: 680+ arrests, nearly 2,400 vehicles seized"),
    ("Los Angeles", "Magnitude 4.2 quake near Commerce"),
    ("US", "Router outage ground stop disrupts 18,000+ flights"),
    ("Rome", "Trajan's Ulpia library ruins reopen after restoration"),
    ("Antalya", "About 50 protesters demonstrate at the closing plenary"),
    ("Portugal", "Zero VAT on basic food basket confirmed for Q1 2027"),
    ("Sines", "Magnitude 3.4 quake strikes 55 km offshore"),
    ("Taiz", "More than 140 civilians killed since August, BBC reports"),
    ("Poland", "11-country drill for a postwar Ukraine mission"),
    ("Poland", "Air-raid alerts issued in Lublin and Podkarpackie"),
    ("Europe", "Workers and students protest wages and living costs"),
]

NUMBERS = [
    ("3+", "killed in the Kyiv strikes"),
    ("250,000+", "lines of Lean in the claimed proof"),
    ("105,000", "evacuated ahead of Cyclone Akvan"),
    ("~300", "missing after the Bayelsa capsize"),
    ("193", "Houthi fighters killed or injured"),
    ("18,000+", "flights hit by the FAA ground stop"),
]

MASTHEAD = "The World Ledger"
DATE_LINE = "Friday 20 November 2026"
FOOTER = ("Sources: AP · BBC · Nature · AFP · Al Jazeera · Arab News · Daily Trust · "
          "New Straits Times · Adnkronos · La Prensa Gráfica · IMD bulletins · "
          "local and regional press · agency wires")

N_STORIES = len(HEROES) + len(MEDIUM) + len(BRIEFS)


# ---------------------------------------------------------------- text engine
class Page:
    def __init__(self):
        self.img = Image.new("RGB", (W, H), PAPER)
        self.d = ImageDraw.Draw(self.img)
        self.manifest = []      # every drawn text run: story, cell, bbox, text
        self.errors = []

    def rule(self, x0, y0, x1, y1, fill=RULE, width=1):
        self.d.rectangle([x0, y0, x1, y1], fill=fill)

    def _record(self, story, cell, bbox, text, size):
        x0, y0, x1, y1 = bbox
        cx0, cy0, cx1, cy1 = cell
        tol = 0.75
        if x0 < cx0 - tol or y0 < cy0 - tol or x1 > cx1 + tol or y1 > cy1 + tol:
            self.errors.append(
                f"OVERFLOW {story!r}: bbox {bbox} outside cell {cell}: {text!r}")
        self.manifest.append(dict(story=story, cell=list(cell),
                                  bbox=[round(v, 2) for v in bbox],
                                  text=text, size=size))

    def text(self, story, cell, x, y, s, f, fill, anchor="lt"):
        bbox = self.d.textbbox((x, y), s, font=f, anchor=anchor)
        self._record(story, cell, bbox, s, f.size)
        self.d.text((x, y), s, font=f, fill=fill, anchor=anchor)
        return bbox

    def wrap(self, s, f, maxw):
        lines, cur = [], ""
        for word in s.split():
            trial = (cur + " " + word).strip()
            if f.getlength(trial) <= maxw or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines

    def para(self, story, cell, x, y, s, maxw, family, bold, size, min_size,
             max_lines, fill, lh=None):
        """Wrap into <= max_lines lines, shrinking the font until it fits."""
        while True:
            f = font(family, bold, size)
            lines = self.wrap(s, f, maxw)
            fits = (len(lines) <= max_lines and
                    all(f.getlength(l) <= maxw + 0.5 for l in lines))
            if fits or size <= min_size:
                break
            size -= 1
        if not fits:
            self.errors.append(f"PARA-OVERFLOW {story!r}: {s!r} "
                               f"({len(lines)} lines at {size}px)")
        lh = lh or int(round(size * 1.28))
        for i, l in enumerate(lines):
            self.text(story, cell, x, y + i * lh, l, f, fill)
        return y + len(lines) * lh, size

    def one_line(self, story, cell, x, y, s, maxw, family, bold, size,
                 min_size, fill):
        """Single line, shrinking until it fits the width."""
        while True:
            f = font(family, bold, size)
            if f.getlength(s) <= maxw + 0.5 or size <= min_size:
                break
            size -= 1
        if f.getlength(s) > maxw + 0.5:
            self.errors.append(f"LINE-OVERFLOW {story!r}: {s!r} at {size}px")
        self.text(story, cell, x, y, s, f, fill)
        return f.size


# ---------------------------------------------------------------- page build
def build():
    p = Page()
    d = p.d

    # ---- masthead
    mast_cell = (M, 10, W - M, 118)
    f = font("serif", True, 37)
    p.text("masthead", mast_cell, W / 2, 14, MASTHEAD, f, INK, anchor="mt")
    p.rule(M, 62, W - M, 63, fill=INK)
    p.rule(M, 66, W - M, 66, fill=RULE)
    f = font("serif", True, 21)
    p.text("date", mast_cell, W / 2, 72, DATE_LINE, f, ACCENT, anchor="mt")
    edition = f"World edition · {N_STORIES} stories · One page, the day's wires"
    f = font("sans", False, 10)
    if f.getlength(edition) > CW:
        f = font("sans", False, 9)
    ew = f.getlength(edition)
    p.text("edition", mast_cell, (W - ew) / 2, 100, edition, f, SECOND)
    p.rule(M, 117, W - M, 117, fill=RULE)

    # ---- heroes: 3 columns
    hy0, hy1 = 123, 331
    gap = 18
    colw = (CW - 2 * gap) // 3          # 314
    widths = [colw, colw, CW - 2 * gap - 2 * colw]
    xs = [M, M + widths[0] + gap, M + widths[0] + gap + widths[1] + gap]
    for i, h in enumerate(HEROES):
        x0, w = xs[i], widths[i]
        cell = (x0, hy0, x0 + w, hy1)
        sid = f"hero{i+1}"
        if i:
            p.rule(x0 - gap // 2, hy0 + 2, x0 - gap // 2, hy1 - 2)
        y = hy0 + 2
        tx = x0 + 1  # guard against 1px negative left side bearings
        y = p.para(sid, cell, tx, y, h["field"], w - 1, "sans", True, 11, 10, 1,
                   ACCENT, lh=14)[0]
        y += 4
        y, _ = p.para(sid, cell, tx, y, h["headline"], w - 1, "serif", True, 26,
                      22, 3, INK, lh=31)
        y += 7
        y, _ = p.para(sid, cell, tx, y, h["summary"], w - 1, "sans", False, 12,
                      10, 3, INK, lh=16)
        y += 8
        y = p.para(sid, cell, tx, y, h["place"], w - 1, "sans", True, 10, 9, 1,
                   SECOND, lh=13)[0]
        y += 2
        p.para(sid, cell, tx, y, "Source: " + h["source"], w - 1, "sans", False,
               9, 8, 1, SECOND, lh=12)
    p.rule(M, hy1 + 3, W - M, hy1 + 3, fill=RULE)

    # ---- by the numbers
    ny0, ny1 = 340, 408
    num_cell = (M, ny0, W - M, ny1)
    p.text("numbers", num_cell, M, ny0 + 3, "By the numbers",
           font("sans", True, 11), SECOND)
    n = len(NUMBERS)
    seg = CW / n
    for i, (value, label) in enumerate(NUMBERS):
        x0 = M + i * seg
        cell = (x0, ny0 + 17, x0 + seg - 6, ny1)
        if i:
            p.rule(int(x0) - 3, ny0 + 18, int(x0) - 3, ny1 - 4)
        p.one_line(f"num{i+1}", cell, x0, ny0 + 18, value, seg - 10,
                   "serif", True, 21, 16, ACCENT)
        p.para(f"num{i+1}", cell, x0, ny0 + 44, label, seg - 10, "sans",
               False, 9, 8, 2, INK, lh=11)
    p.rule(M, ny1 + 3, W - M, ny1 + 3, fill=RULE)

    # ---- medium cards: 4 x 3 grid
    my0, my1 = 417, 737
    gx, gy = 14, 6
    cols = 4
    rows = 3
    cw = (CW - (cols - 1) * gx) / cols
    rh = (my1 - my0 - (rows - 1) * gy) / rows
    for idx, m in enumerate(MEDIUM):
        r, c = divmod(idx, cols)
        x0 = M + c * (cw + gx)
        y0 = my0 + r * (rh + gy)
        cell = (x0, y0, x0 + cw, y0 + rh)
        sid = f"med{idx+1}"
        d.rectangle([x0, y0, x0 + cw, y0 + rh], outline=RULE, width=1)
        pad = 8
        iw = cw - 2 * pad
        y = y0 + 8
        p.one_line(sid, cell, x0 + pad, y, m["field"], iw, "sans", True, 9,
                   8, SECOND)
        y += 14
        y, _ = p.para(sid, cell, x0 + pad, y, m["headline"], iw, "serif",
                      True, 15, 13, 2, INK, lh=18)
        y += 5
        p.one_line(sid, cell, x0 + pad, y, m["line"], iw, "sans", False, 10,
                   9, INK)
        y += 15
        p.one_line(sid, cell, x0 + pad, y, m["place"], iw, "sans", False, 9,
                   8, SECOND)
    p.rule(M, my1 + 3, W - M, my1 + 3, fill=RULE)

    # ---- briefs: 3 columns x 8 rows, one line each
    by0, by1 = 746, 1001
    p.text("briefs-header", (M, by0, W - M, by0 + 16), M, by0 + 1, "Briefs",
           font("sans", True, 11), SECOND)
    p.rule(M, by0 + 16, W - M, by0 + 16, fill=RULE)
    bgap = 16
    bcols = 3
    bcw = (CW - (bcols - 1) * bgap) / bcols
    top = by0 + 20
    rowh = (by1 - top) / 8
    for i, (place, txt) in enumerate(BRIEFS):
        c, r = divmod(i, 8)
        x0 = M + c * (bcw + bgap)
        y0 = top + r * rowh
        cell = (x0, y0, x0 + bcw, y0 + rowh)
        sid = f"brief{i+1}"
        if c:
            p.rule(int(x0 - bgap / 2), int(top), int(x0 - bgap / 2), int(by1 - 2))
        if r:
            p.rule(x0 + 1, y0, x0 + bcw - 1, y0, fill=RULE)
        # place prefix (bold, secondary) + em dash + text (ink), one line
        size = 10
        while size > 8:
            fb = font("sans", True, size)
            fr = font("sans", False, size)
            prefix = place + " — "
            if fb.getlength(prefix) + fr.getlength(txt) <= bcw - 4:
                break
            size -= 1
        fb = font("sans", True, size)
        fr = font("sans", False, size)
        prefix = place + " — "
        total = fb.getlength(prefix) + fr.getlength(txt)
        if total > bcw - 4 + 0.5:
            p.errors.append(f"BRIEF-OVERFLOW {sid}: {prefix+txt!r} at {size}px")
        ty = y0 + (rowh - size) / 2 - 1
        p.text(sid, cell, x0 + 2, ty, prefix, fb, SECOND)
        p.text(sid, cell, x0 + 2 + fb.getlength(prefix), ty, txt, fr, INK)

    # ---- footer
    p.rule(M, 1005, W - M, 1005, fill=INK)
    foot_cell = (M, 1007, W - M, 1022)
    f = font("sans", False, 8)
    fw = f.getlength(FOOTER)
    if fw > CW:
        f = font("sans", False, 7)
        fw = f.getlength(FOOTER)
    p.text("footer", foot_cell, (W - fw) / 2, 1009, FOOTER, f, SECOND)

    return p


def main():
    p = build()
    if p.errors:
        print("LAYOUT ERRORS:", file=sys.stderr)
        for e in p.errors:
            print(" ", e, file=sys.stderr)
        raise SystemExit(1)
    out = os.path.join(ROOT, "entry.png")
    p.img.save(out, "PNG", optimize=True)
    size = os.path.getsize(out)
    print(f"wrote {out}: {p.img.size[0]}x{p.img.size[1]}, {size} bytes "
          f"({size/1048576:.3f} MiB)")
    print(f"stories: {len(HEROES)} heroes + {len(MEDIUM)} medium + "
          f"{len(BRIEFS)} briefs = {N_STORIES}")
    print(f"text runs drawn: {len(p.manifest)}; all boxes asserted inside cells")
    if "--text" in sys.argv:
        print("\n--- page text ---")
        for item in p.manifest:
            print(f"[{item['story']}] {item['text']}")
    if "--manifest" in sys.argv:
        import json
        print(json.dumps(p.manifest, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()