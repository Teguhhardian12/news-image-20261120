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
# Compound items are split into separate stories; no fact is invented and no
# fact is moved to a day it did not happen on.
HEROES = [
    dict(
        field="Conflict",
        headline="At least 3 killed as missiles hit Kyiv",
        summary=("About 12 ballistic missiles and drones struck the Ukrainian "
                 "capital overnight, killing at least 3 people."),
        place="Kyiv, Ukraine",
        source="AP",
    ),
    dict(
        field="Science and AI",
        headline="Anthropic mathematician claims Riemann proof",
        summary=("Levent Alpöge says six weeks working with Claude produced a "
                 "proof of the Riemann hypothesis, a day after Anthropic's "
                 "market debut."),
        place="Anthropic",
        source="BBC · Nature · AFP",
    ),
    dict(
        field="Climate",
        headline="COP31 closes without the words fossil fuels",
        summary=("The closing draft at the Antalya talks dropped every mention "
                 "of fossil fuels on the final day of the UN climate talks."),
        place="Antalya",
        source="AP",
    ),
]

MEDIUM = [
    dict(field="Conflict", headline="Two Russian missiles fall in Poland",
         line="A Kh-101 hit a field near Nowy Lipowiec", place="Lublin, Poland"),
    dict(field="Labour", headline="Italy stops for a 24-hour general strike",
         line="About 100 squares march against the budget", place="Rome · Italy"),
    dict(field="Labour", headline="Portugal's public sector walks out",
         line="Strike timed to the 2027 budget vote", place="Portugal"),
    dict(field="Shipping", headline="Tanker ablaze in the Strait of Hormuz",
         line="IRGC and UKMTO report fire off Khasab", place="Khasab, Oman"),
    dict(field="Conflict", headline="Saudi-led coalition strikes Yemen",
         line="Hodeidah, Sanaa, Saada and Taiz hit", place="Yemen"),
    dict(field="Security", headline="Iraq agrees joint ops with Kata'ib Hezbollah",
         line="Al-Zaidi: joint centre and troops deployed", place="Jurf al-Sakhar"),
    dict(field="Disaster", headline="30 dead as funeral boat capsizes",
         line="Around 300 missing in Bayelsa State", place="Nigeria"),
    dict(field="Seismic", headline="Magnitude 6.7 quake hits central Peru",
         line="Felt in Lima; no fatalities reported", place="30 km north-west of Junín"),
    dict(field="Rights", headline="UN court finds genocide in Myanmar",
         line="Rights groups urge sanctions after the ruling", place="Myanmar · United Nations"),
    dict(field="Markets", headline="Seventh straight fall for Asia stocks",
         line="Nikkei -4.6%; Kospi below 5,000", place="Tokyo · Seoul"),
    dict(field="Weather", headline="Cyclone Akvan bears down on Odisha",
         line="Landfall near Gopalpur around noon IST", place="Odisha, India"),
    dict(field="Tech policy", headline="Trump threatens tax on AI data centres",
         line="A tremendous tax if built abroad, he says", place="Washington"),
    dict(field="Diplomacy", headline="UK and EU rebuild post-Brexit ties",
         line="Trade and travel deals at a rare summit", place="London · Brussels"),
    dict(field="Conflict", headline="Yemen ops kill or injure 193 Houthis",
         line="Government forces in Al-Jawf, Marib, Taiz", place="Yemen"),
    dict(field="Tech policy", headline="Senate passes data-centre permitting bill",
         line="Faster reviews; centres to pay energy costs", place="Washington"),
    dict(field="Markets", headline="Global stocks head for longest slide since 2023",
         line="MSCI Asia-Pacific down 1.1% for a seventh day", place="World markets"),
]

BRIEFS = [
    ("Kyiv", "Bridges were crippled and power cut in the overnight attack"),
    ("Lublin", "Air-raid alerts issued in Lublin and Podkarpackie after the falls"),
    ("Nowy Lipowiec", "The Kh-101 fell about 60 miles from the Coalition drill"),
    ("Warsaw", "The prime minister called it likely an intentional provocation"),
    ("Poland", "Troops from 11 countries drilled for a postwar Ukraine mission"),
    ("NATO", "Called the fall of Russian missiles in Poland a violation"),
    ("Anthropic", "Alpöge says the generalized Riemann hypothesis is proved too"),
    ("Anthropic", "A four-page sketch of the proof was released on Friday"),
    ("Anthropic", "The Lean version runs to more than 250,000 lines"),
    ("Andrew Granville", "Called the write-up of the claimed proof garbled"),
    ("Terence Tao", "Said verification of the proof is still some way off"),
    ("Maynard", "Suspects it is correct; checking the Lean will take time"),
    ("Antalya", "The closing draft dropped the $120bn adaptation figure"),
    ("Antalya", "About 50 protesters held Shame signs at the closing plenary"),
    ("Antalya", "Leaders called the climate process hypocritical and futile"),
    ("Antalya", "The final text of the talks was due at midnight"),
    ("Rome", "Maurizio Landini closed the march from Piazza Vittorio Emanuele II"),
    ("Italy", "CGIL's strike stopped transport, schools and hospitals"),
    ("Italy", "Strikers demanded wages, pensions, healthcare and housing"),
    ("Italy", "Marchers called for yes to peace, no to rearmament"),
    ("Europe", "Workers and students protested stagnant wages and living costs"),
    ("Lisbon", "Unions demand at least 15%, at least €150 a month, from January"),
    ("Lisbon", "A €1,150 minimum public-sector wage is sought from Jan 2027"),
    ("Portugal", "Rubbish collection stopped in several municipalities"),
    ("Portugal", "Schools closed and hospitals ran on minimum services"),
    ("Portugal", "Parliament confirmed zero VAT on the basic food basket for Q1"),
    ("Sines", "A magnitude 3.4 quake struck offshore, 55 km to the west"),
    ("Hodeidah", "The coalition said it was targeting weapons smuggling"),
    ("Taiz", "More than 140 civilians killed since August, the BBC reports"),
    ("Baghdad", "Al-Zaidi had threatened to send forces into the stronghold"),
    ("Jurf al-Sakhar", "Government and Kata'ib Hezbollah troops to station jointly"),
    ("El Salvador", "Three soldiers killed, one injured, as explosives detonated"),
    ("Haiti · El Salvador", "Three new prisons agreed to hold Haitian gang members"),
    ("Myanmar", "Dismissed the genocide ruling as unfair"),
    ("United Nations", "China and Russia could veto any Security Council action"),
    ("Odisha", "About 105,000 evacuated; some reports say 300,000 in all"),
    ("Odisha", "Winds of 90–100 km/h, gusting higher, forecast at landfall"),
    ("Odisha", "More than 400 rescue teams deployed; dozens of trains cancelled"),
    ("Alaska", "The DOJ moved to drop its suit over Mary Peltola's Senate win"),
    ("Malaysia", "Anwar: air-force officers, pilots included, suspected of drugs"),
    ("France", "Dominique de Villepin will run in the 2027 presidential election"),
    ("Wellington", "New Zealand 317-6 v India: Phillips 118, Nicholls 146 not out"),
    ("Turin", "The ATP Finals group stage ended"),
    ("Las Vegas", "The Grand Prix was washed out"),
    ("Hong Kong", "India beat Malaysia in the Hong Kong Open"),
    ("US", "FBI warned of a surge in sextortion of minors, a record year"),
    ("Cincinnati", "Fiona the hippo died days after eating a visitor's hat"),
    ("WWE", "Dwayne Johnson announced his return"),
    ("US Capitol", "A 76-foot Engelmann spruce arrived after a 2,000-mile journey"),
    ("Interpol", "Carback II: 680+ arrests, almost 2,400 vehicles seized"),
    ("Los Angeles", "A magnitude 4.2 earthquake near Commerce shook the city"),
    ("US", "An FAA ground stop from a router outage hit 18,000+ flights"),
    ("US", "The root cause of the router outage is due this week"),
    ("Rome", "The ruins of Trajan's Ulpia library opened after restoration"),
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
        self.brief_size = 9
        self.brief_lead = 12
        self.briefs_top = 0
        self.medium_bottom = 0

    def rule(self, x0, y0, x1, y1, fill=RULE, width=1):
        self.d.rectangle([x0, y0, x1, y1], fill=fill)

    def bar(self, story, y, h, label, right=None):
        """Solid ink section flag with reversed (paper) text."""
        cell = (M, y, W - M, y + h)
        self.d.rectangle([M, y, W - M, y + h], fill=INK)
        f = font("sans", True, 11)
        self.text(story, cell, M + 8, y + (h - 11) / 2 - 1, label, f, PAPER)
        if right:
            fr = font("sans", False, 10)
            rw = fr.getlength(right)
            self.text(story, cell, W - M - 8 - rw, y + (h - 10) / 2 - 1,
                      right, fr, PAPER)
        return y + h

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


# ---------------------------------------------------------------- briefs grid
BCOLS = 6
BGAP = 12
BCW = (CW - (BCOLS - 1) * BGAP) / BCOLS
BLEAD = 12          # 11-12 px leading
BMAXLINES = 3


def brief_lines(size):
    """Wrap every brief at the given serif-bold size; return list of line-lists."""
    f = font("serif", True, size)
    pg = Page()
    out = [pg.wrap(place + " — " + txt, f, BCW - 4) for place, txt in BRIEFS]
    return out


def choose_brief_size():
    for size in (9, 8):
        ls = brief_lines(size)
        if all(len(l) <= BMAXLINES for l in ls):
            return size, ls
    return 8, brief_lines(8)


# ---------------------------------------------------------------- page build
def build():
    p = Page()

    # ---- masthead
    mast_cell = (M, 8, W - M, 106)
    f = font("serif", True, 38)
    p.text("masthead", mast_cell, W / 2, 12, MASTHEAD, f, INK, anchor="mt")
    p.rule(M, 58, W - M, 59, fill=INK)          # thin rule under the name
    f = font("serif", True, 22)
    p.text("date", mast_cell, W / 2, 64, DATE_LINE, f, ACCENT, anchor="mt")
    edition = f"World edition · {N_STORIES} stories · One page, the day's wires"
    f = font("sans", False, 10)
    if f.getlength(edition) > CW:
        f = font("sans", False, 9)
    ew = f.getlength(edition)
    p.text("edition", mast_cell, (W - ew) / 2, 90, edition, f, SECOND)
    p.rule(M, 104, W - M, 104, fill=RULE)

    # ---- heroes: 3 columns
    hy0, hy1 = 112, 302
    gap = 18
    colw = (CW - 2 * gap) // 3
    widths = [colw, colw, CW - 2 * gap - 2 * colw]
    xs = [M, M + widths[0] + gap, M + widths[0] + gap + widths[1] + gap]
    for i, h in enumerate(HEROES):
        x0, w = xs[i], widths[i]
        cell = (x0, hy0, x0 + w, hy1)
        sid = f"hero{i+1}"
        if i:
            p.rule(x0 - gap // 2, hy0 + 2, x0 - gap // 2, hy1 - 2)
        y = hy0 + 2
        tx = x0 + 1
        y = p.para(sid, cell, tx, y, h["field"], w - 1, "sans", True, 11, 10, 1,
                   ACCENT, lh=14)[0]
        y += 4
        y, _ = p.para(sid, cell, tx, y, h["headline"], w - 1, "serif", True, 25,
                      22, 3, INK, lh=29)
        y += 7
        y, _ = p.para(sid, cell, tx, y, h["summary"], w - 1, "sans", False, 12,
                      10, 3, INK, lh=15)
        y += 8
        y = p.para(sid, cell, tx, y, h["place"], w - 1, "sans", True, 10, 9, 1,
                   SECOND, lh=13)[0]
        y += 2
        p.para(sid, cell, tx, y, "Source: " + h["source"], w - 1, "sans", False,
               9, 8, 1, SECOND, lh=12)
    p.rule(M, 305, W - M, 305, fill=RULE)

    # ---- by the numbers (solid flag + figures)
    ny = p.bar("numbers-flag", 310, 14, "By the numbers")
    ny0, ny1 = ny + 4, 380
    n = len(NUMBERS)
    seg = CW / n
    for i, (value, label) in enumerate(NUMBERS):
        x0 = M + i * seg
        cell = (x0, ny0, x0 + seg - 6, ny1)
        if i:
            p.rule(int(x0) - 3, ny0 + 2, int(x0) - 3, ny1 - 2)
        p.one_line(f"num{i+1}", cell, x0, ny0 + 2, value, seg - 10,
                   "serif", True, 21, 16, ACCENT)
        p.para(f"num{i+1}", cell, x0, ny0 + 28, label, seg - 10, "sans",
               False, 9, 8, 2, INK, lh=11)
    p.rule(M, 382, W - M, 382, fill=RULE)

    # ---- medium cards: 4 x 4 grid (field + headline + one line)
    my0 = 386
    gx, gy = 12, 6
    cols, rows = 4, 4
    cw = (CW - (cols - 1) * gx) / cols
    rh = 62
    for idx, m in enumerate(MEDIUM):
        r, c = divmod(idx, cols)
        x0 = M + c * (cw + gx)
        y0 = my0 + r * (rh + gy)
        cell = (x0, y0, x0 + cw, y0 + rh)
        sid = f"med{idx+1}"
        p.d.rectangle([x0, y0, x0 + cw, y0 + rh], outline=RULE, width=1)
        pad = 6
        iw = cw - 2 * pad
        p.one_line(sid, cell, x0 + pad, y0 + 4, m["field"], iw, "sans", True, 9,
                   8, SECOND)
        p.para(sid, cell, x0 + pad, y0 + 15, m["headline"], iw, "serif",
               True, 14, 13, 2, INK, lh=15)
        p.one_line(sid, cell, x0 + pad, y0 + 47, m["line"], iw, "sans", False,
                   10, 9, INK)
    medium_bottom = my0 + rows * rh + (rows - 1) * gy
    p.rule(M, medium_bottom + 3, W - M, medium_bottom + 3, fill=RULE)

    # ---- briefs: 6 columns, row-major bands, aligned baselines, fill to bottom
    by1 = 1002                                   # bottom margin of the block
    header_h = 14
    chosen = None
    for bsize, lead in ((9, 12), (9, 11), (8, 12), (8, 11)):
        blines = brief_lines(bsize)
        if not all(len(l) <= BMAXLINES for l in blines):
            continue
        nrows = (len(BRIEFS) + BCOLS - 1) // BCOLS
        row_heights = [max(len(c) for c in blines[r * BCOLS:(r + 1) * BCOLS])
                       * lead for r in range(nrows)]
        rows_h = sum(row_heights)
        top = by1 - (header_h + 3 + rows_h)
        if top >= medium_bottom + 6:
            chosen = (bsize, lead, blines, nrows, row_heights, rows_h, top)
            break
    if chosen is None:
        p.errors.append("BRIEFS-FIT: no size/leading fits above the medium grid")
        chosen = (8, 11, brief_lines(8), 1, [0], 0, by1)
    bsize, lead, blines, nrows, row_heights, rows_h, briefs_top = chosen
    fb = font("serif", True, bsize)
    p.bar("briefs-flag", briefs_top, header_h, "Briefs",
          right=f"{len(BRIEFS)} one-line stories")
    top = briefs_top + header_h + 3
    for c in range(1, BCOLS):                    # vertical rules between columns
        x = M + c * (BCW + BGAP) - BGAP / 2
        p.rule(int(x), top, int(x), by1 - 1)
    y = top
    for r in range(nrows):
        rh = row_heights[r]
        for c in range(BCOLS):
            i = r * BCOLS + c
            if i >= len(BRIEFS):
                break
            x0 = M + c * (BCW + BGAP)
            cell = (x0, y, x0 + BCW, y + rh)
            sid = f"brief{i+1}"
            place, txt = BRIEFS[i]
            prefix = place + " — "
            for k, ln in enumerate(blines[i]):
                ly = y + k * lead
                if k == 0 and ln.startswith(prefix):
                    p.text(sid, cell, x0 + 2, ly, prefix, fb, SECOND)
                    p.text(sid, cell, x0 + 2 + fb.getlength(prefix), ly,
                           ln[len(prefix):], fb, INK)
                else:
                    p.text(sid, cell, x0 + 2, ly, ln, fb, INK)
        p.rule(M, y + rh - 2, W - M, y + rh - 2, fill=SECOND)
        y += rh
    if y != by1:
        p.errors.append(f"BRIEFS-BOTTOM: block ends {y}, expected {by1}")

    # ---- footer
    p.rule(M, 1005, W - M, 1005, fill=INK)
    foot_cell = (M, 1007, W - M, 1022)
    f = font("sans", False, 8)
    fw = f.getlength(FOOTER)
    if fw > CW:
        f = font("sans", False, 7)
        fw = f.getlength(FOOTER)
    p.text("footer", foot_cell, (W - fw) / 2, 1009, FOOTER, f, SECOND)

    p.brief_size = bsize
    p.brief_lead = lead
    p.briefs_top = briefs_top
    p.medium_bottom = medium_bottom
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
    print(f"briefs: {p.brief_size}px serif bold, 6 cols, leading {p.brief_lead}, "
          f"top={p.briefs_top}, medium_bottom={p.medium_bottom}")
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
