# The World Ledger — Friday 20 November 2026

A single-image newspaper front page summarizing the world news of **Friday
20 November 2026**. One 1024×1024 PNG (`entry.png`, ~163 KiB), light
newsprint palette, strict grid, no story invented: every line on the page
comes from the researched and attributed brief for that day.

## The page

- **Masthead** — paper name, the date "Friday 20 November 2026" printed once
  in headline red, and an edition line.
- **3 heroes** — Russia's missile strikes on Kyiv and the missiles that fell
  in Poland (AP); Anthropic mathematician Levent Alpöge's claimed Riemann
  hypothesis proof built with Claude (BBC, Nature, AFP); COP31's closing day
  in Antalya without fossil-fuel language (AP). Each with field label,
  headline, summary, place line and source line.
- **By the numbers** — 6 figures drawn from the stories: 3+ killed in Kyiv,
  250,000+ Lean lines, 105,000 evacuated before Cyclone Akvan, ~300 missing
  in Bayelsa, 193 Houthi fighters killed or injured, 18,000+ flights disrupted.
- **12 medium cards** (4×3 grid) — Italy's general strike, Portugal's
  public-sector strike, the Hormuz tanker fire, Yemen strikes, Iraq's pact
  with Kata'ib Hezbollah, the Bayelsa boat disaster, Peru's magnitude 6.7
  quake, the UN court's Rohingya genocide finding, Asia's markets slide,
  Cyclone Akvan, Washington's AI data-centre tax threat, the UK–EU summit.
- **24 briefs** (3 columns × 8 rows, one line each) — Haiti/El Salvador
  prisons, the Salvadoran soldiers' deaths, Alaska/Peltola, Malaysia,
  France/Villepin, sport (Wellington cricket, ATP Finals, Las Vegas GP,
  Hong Kong Open), FBI sextortion warning, Fiona the hippo, Dwayne Johnson's
  WWE return, the Capitol spruce, Interpol Carback II, the Los Angeles quake,
  the FAA ground stop, Trajan's library, the Antalya protesters, Portugal's
  zero VAT and Sines quake, Taiz, the Poland drill and air-raid alerts, and
  European wage protests.

**Story count: 39** (3 heroes + 12 medium cards + 24 briefs).

## Sources

All facts were researched beforehand and are attributed on the page:
AP, BBC, Nature, AFP, Al Jazeera, Arab News, Daily Trust, New Straits Times,
Adnkronos, La Prensa Gráfica, IMD bulletins via Indian press, local and
regional press, and agency wires. No fact appears on the page that is not in
the source brief; no network access is used at build or run time.

## How it is built

- Renderer: **Pillow 13.0.0** (it was installed, so it was used), with DejaVu
  Serif / DejaVu Sans from `/usr/share/fonts/truetype/dejavu`.
- `tools/render.py` draws the page deterministically — no clock, no
  randomness, no network. Every string is measured with the actual font,
  wrapped or shrunk deliberately, and each drawn bounding box is asserted to
  fit its cell (154 text runs, 0 overflows). Re-rendering reproduces
  `entry.png` byte-for-byte.
- `entry.png` — 1024×1024, RGB, 166,952 bytes (0.159 MiB < 1 MiB).
  sha256: `d27caeec5429fd78295c67b7d53ca7662b3090ad62f1b52ca4ae66c8eba81be0`

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

- `PIL.Image.open('entry.png')` → `(1024, 1024) RGB`; 166,952 bytes on disk.
- All 154 drawn text bounding boxes asserted inside their cells; 0 violations.
- Page rendered to text and audited: 39 stories, date printed exactly once.
- Determinism: a fresh render is byte-identical to the committed PNG.
- `main.py` tested with `python3 -P -s` from a foreign cwd against a
  read-only copy of the repo: output byte-identical (`cmp` clean).
- Negative tests: truncated and CRC-corrupted PNGs are rejected (exit 1).