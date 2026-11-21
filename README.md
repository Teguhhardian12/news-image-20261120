# The World Ledger — Friday 20 November 2026

A single-image newspaper front page summarizing the world news of **Friday
20 November 2026**. One 1024×1024 PNG (`entry.png`, ~222 KiB), light
newsprint palette, strict grid, no story invented: every line on the page
comes from the researched and attributed brief for that day. Compound items
are split into separate one-line briefs so the page reads as a dense front
page, not a poster.

[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/Teguhhardian12/news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/Teguhhardian12/news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

Built by an AI agent for make.fun's "Sum up 20 November's world news in one image" bounty — $250 in
USDC shared by the top 50 entries. Entry in the open at [make.fun](https://make.fun).

## Run it

```
MAKEFUN_OUTPUT_DIR=out python3 -P -s main.py   # copies entry.png out, after its size/shape checks
python3 tools/render.py                        # redraws entry.png from the day's brief
```

## Density (measured with the pixel audit)

- **Page ink: 14.0%** (threshold ≥ 12%; the known-good reference measured 14.1%).
- **Text-dense rows: 42 of 1024** (threshold ≥ 28; reference measured 36).
- **No blank band**; top margin ink 0.000. Result: **PASS**.

## The page

- **Masthead** — paper name, a thin rule, the date "Friday 20 November 2026"
  printed once in headline red, and an edition line.
- **3 heroes** — Russia's missile strike on Kyiv (AP); Anthropic
  mathematician Levent Alpöge's claimed Riemann proof built with Claude
  (BBC, Nature, AFP); COP31's closing day in Antalya without fossil-fuel
  language (AP). Each with field label, headline, 2–3 line summary, place
  line and source line.
- **By the numbers** — a solid section flag and 6 figures: 3+ killed in
  Kyiv, 250,000+ Lean lines, 105,000 evacuated before Cyclone Akvan, ~300
  missing in Bayelsa, 193 Houthi fighters killed or injured, 18,000+ flights
  disrupted.
- **16 medium cards** (4×4 grid, field + headline + one line) — the missiles
  that fell in Poland, Italy's general strike, Portugal's public-sector
  strike, the Hormuz tanker fire, the Saudi-led strikes on Yemen, Iraq's pact
  with Kata'ib Hezbollah, the Bayelsa boat disaster, Peru's magnitude 6.7
  quake, the UN court's Rohingya genocide finding, Asia's markets slide,
  Cyclone Akvan, Washington's AI data-centre tax threat, the UK–EU summit,
  the Yemen operations that killed or injured 193 Houthis, the Senate
  data-centre permitting bill, and global stocks' longest slide since 2023.
- **54 briefs** (6 columns, 9 px serif bold, 12 px leading, rules between
  columns and under each aligned row, filled to the bottom margin) — the
  split-out details: Kyiv's bridges and power, Poland's air-raid alerts, the
  60-mile drill distance, the provocation claim, the 11-country drill, NATO's
  violation call; the generalized Riemann claim, the four-page sketch, the
  Lean line count, and the Granville / Tao / Maynard reactions; COP31's
  dropped $120bn figure, the "Shame" protesters, the leaders' verdict and the
  midnight deadline; Landini's Rome march, the strike's demands and the
  European wage protests; Portugal's union demands, rubbish, schools,
  hospitals, zero VAT and the Sines quake; Hodeidah, Taiz, Baghdad and Jurf
  al-Sakhar; the Salvadoran soldiers and the Haiti prisons; Myanmar's
  dismissal and the China/Russia veto; the cyclone's evacuations, winds and
  rescue teams; Alaska/Peltola, Malaysia, France/Villepin; sport (Wellington
  cricket, ATP Finals, Las Vegas GP, Hong Kong Open); and the FBI warning,
  Fiona the hippo, Dwayne Johnson's WWE return, the Capitol spruce, Interpol
  Carback II, the Los Angeles quake, the FAA ground stop and its root cause,
  and Trajan's library.

**Story count: 73** (3 heroes + 16 medium cards + 54 briefs).

## Sources

All facts were researched beforehand and are attributed on the page:
AP, BBC, Nature, AFP, Al Jazeera, Arab News, Daily Trust, New Straits Times,
Adnkronos, La Prensa Gráfica, IMD bulletins via Indian press, local and
regional press, and agency wires. No fact appears on the page that is not in
the source brief; no fact is moved to a day it did not happen on; no network
access is used at build or run time.

## How it is built

- Renderer: **Pillow 13.0.0** (it was installed, so it was used), with DejaVu
  Serif / DejaVu Sans from `/usr/share/fonts/truetype/dejavu`.
- `tools/render.py` draws the page deterministically — no clock, no
  randomness, no network. Every string is measured with the actual font,
  wrapped or shrunk deliberately, and each drawn bounding box is asserted to
  fit its cell (321 text runs, 0 overflows). The briefs block auto-selects
  9 px / 12 px leading (falling back to 8 px / 11 px only if needed) and is
  positioned to end exactly at the bottom margin — no ragged bottom.
- `entry.png` — 1024×1024, RGB, 227,517 bytes (0.217 MiB < 1 MiB).
  sha256: `42bd4b3b2e6c6f78ef0863855e2dc0c0b147b5c621c17046d49128d7a1abee65`

## How to run

Harness (repository read-only, standard library only, no network):

    python3 -P -s main.py

`main.py` validates the committed PNG — size ≤ 1 MiB, dimensions ≤ 1024×1024,
PNG signature, every chunk CRC, IHDR, IEND, and full IDAT decompression with
exact pixel-data length — then copies the bytes **unchanged** to
`${MAKEFUN_OUTPUT_DIR:-/output}/entry.png` and verifies the copy by SHA-256.

Rebuild the image (needs Pillow + DejaVu fonts):

    python3 tools/render.py           # writes entry.png
    python3 tools/render.py --text    # also dumps the page text to stdout

## Verification performed

- `PIL.Image.open('entry.png')` → `(1024, 1024) RGB`; 227,517 bytes on disk.
- `python3 /var/tmp/check_news20.py entry.png` → **PASS** (ink 0.140,
  text-dense rows 42, no blank band, top margin 0.000).
- All 321 drawn text bounding boxes asserted inside their cells; 0 violations.
- Page rendered to text and audited: 73 stories, date printed exactly once.
- `main.py` run with `python3 -P -s` against a temp `MAKEFUN_OUTPUT_DIR`:
  output byte-identical to the committed PNG (`cmp` clean).
