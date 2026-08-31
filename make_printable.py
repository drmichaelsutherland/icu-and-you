#!/usr/bin/env python3
"""
ICU AND YOU — printable superpuzzle generator.

Builds the printable companion for a fillable superpuzzle, using the fillable
page as the single source of truth: the grid geometry comes from its GEOM
array, the clues from its clue lists, and the wording from its own header.

    python3 make_printable.py superpuzzle-49-postneonatal-fillable.html
    python3 make_printable.py --all

Output is named by dropping "-fillable" from the input, matching the
convention already set by superpuzzle-47-transplantation.html.

It also inserts a reciprocal pair of links: "Printable version" on the
fillable, "Fill it in on screen" on the printable.
"""

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CELL = 26          # cell size in SVG units, as set by superpuzzle 47
PAD = 1            # 1px offset so the outer stroke is not clipped

PRINT_LINK = ('<div class="links"><a class="printlink" href="{file}">'
              'Printable version &nbsp;&rarr;</a></div>')

LINK_CSS = """
  .printlink{display:inline-block;margin:14px 0 0;padding:9px 20px;border-radius:20px;
    border:1px solid var(--rust);background:transparent;color:var(--rust);
    text-decoration:none;font:600 12.5px 'Helvetica Neue',Arial,sans-serif;
    letter-spacing:.05em}
  .printlink:hover{background:var(--rust);color:#FDF8F5}
  @media print{ .printlink{display:none} }
"""


def read(p):
    return Path(p).read_text(encoding="utf-8")


def grab(src, pattern, flags=re.S, group=1, required=True, default=None):
    m = re.search(pattern, src, flags)
    if not m:
        if required:
            raise SystemExit(f"could not find: {pattern[:60]}")
        return default
    return m.group(group)


def extract_geometry(src):
    """Geometry as [{n, c:[[x,y],...]}, ...].

    Newer puzzles carry a GEOM array in their script. Superpuzzle 46 predates
    it, so fall back to reading the grid divs, whose inline styles give
    1-based grid-row/grid-column and whose cn spans give the clue numbers.
    """
    m = re.search(r'var GEOM = (\[.*?\]);\s*\n', src, re.S)
    if m:
        return json.loads(m.group(1))

    entries = []
    for div in re.findall(r'<div class="cell" style="([^"]*)"[^>]*>(.*?)</div>',
                          src, re.S):
        style, body = div
        row = int(re.search(r'grid-row:\s*(\d+)', style).group(1)) - 1
        col = int(re.search(r'grid-column:\s*(\d+)', style).group(1)) - 1
        num = re.search(r'<span class="cn">(\d+)</span>', body)
        entries.append((col, row, int(num.group(1)) if num else None))
    if not entries:
        raise SystemExit("no GEOM and no grid cells found")

    # One pseudo-entry per cell; numbered cells carry their number. build_svg
    # only needs the cell set and which cells start an entry.
    return [{"n": n if n else 0, "c": [[x, y]]} for x, y, n in entries]


def build_svg(geom, puzzle_no):
    """Render the grid as SVG: one rect per cell, one number per entry start."""
    cells, starts = set(), {}
    for g in geom:
        for c in g["c"]:
            cells.add(tuple(c))
        if not g["n"]:
            continue          # fallback placeholder: an unnumbered cell
        first = tuple(g["c"][0])
        # two entries can start in the same cell; the lower number wins
        if first not in starts or g["n"] < starts[first]:
            starts[first] = g["n"]

    max_x = max(x for x, _ in cells)
    max_y = max(y for _, y in cells)
    w = (max_x + 1) * CELL + PAD * 2
    h = (max_y + 1) * CELL + PAD * 2

    parts = [
        f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" '
        f'role="img" aria-label="ICU Superpuzzle {puzzle_no} grid">',
        '<style>.cell{fill:#FFFFFF;stroke:#1B2A33;stroke-width:1.4}'
        ".num{font:600 9px 'Helvetica Neue',Arial,sans-serif;fill:#1B2A33}</style>",
    ]
    for x, y in sorted(cells, key=lambda t: (t[0], t[1])):
        px, py = PAD + x * CELL, PAD + y * CELL
        parts.append(f'<rect class="cell" x="{px}" y="{py}" '
                     f'width="{CELL}" height="{CELL}"/>')
        if (x, y) in starts:
            parts.append(f'<text class="num" x="{px + 2.5}" y="{py + 9}">'
                         f'{starts[(x, y)]}</text>')
    parts.append("</svg>")
    return "".join(parts), len(cells), len(starts)


def extract_clues(src):
    """Pull the Across and Down clue lists out of the fillable page.

    The fillable marks clues up as <ul class="clues" id="cA"> with cn/ct
    spans; the printable wants <ol class="clues"> with an n span. This
    reads the former and clue_html() writes the latter.
    """
    out = {}
    for heading, list_id in (("Across", "cA"), ("Down", "cD")):
        block = grab(src, rf'<[uo]l class="clues" id="{list_id}">(.*?)</[uo]l>',
                     required=False)
        if block:
            items = re.findall(r'<li[^>]*>\s*<span class="cn">(\d+)</span>\s*'
                               r'<span class="ct">(.*?)</span>', block, re.S)
        else:
            # superpuzzle 46 style: <div><h2>Across</h2><ul>...
            block = grab(src, rf'<h2>{heading}</h2><ul>(.*?)</ul>')
            items = re.findall(r'<li[^>]*>\s*<span class="cnum">(\d+)</span>\s*'
                               r'<span class="ctxt">(.*?)</span>', block, re.S)
        if not items:
            raise SystemExit(f"no {heading} clues found")
        out[heading] = [(n, t.strip()) for n, t in items]
    return out


def clue_html(clues):
    cols = []
    for heading in ("Across", "Down"):
        lis = "\n".join(
            f'          <li><span class="n">{n}</span><span>{t}</span></li>'
            for n, t in clues[heading]
        )
        cols.append(
            f'      <div class="col">\n'
            f'        <h2 class="sec">{heading}</h2>\n'
            f'        <ol class="clues">\n{lis}\n        </ol>\n'
            f'      </div>'
        )
    return "\n\n".join(cols)


def clues_for_challenge(src):
    return extract_clues(src)


def build_challenge(src, no, clues):
    """Reuse the fillable's own reply button, so the printable sends the same
    email. The usefulness line is appended, as on every other content page."""
    mailto = grab(src, r'href="(mailto:icuandyou@icloud\.com\?subject=[^"]*)"',
                  required=False)
    if not mailto:
        # build one from the clue numbers
        across = "%0D%0A".join(f"{n}%20" for n, _ in clues["Across"])
        down = "%0D%0A".join(f"{n}%20" for n, _ in clues["Down"])
        mailto = (f"mailto:icuandyou@icloud.com?subject=Superpuzzle%20%23{no}"
                  f"%20-%20my%20answers&body=Across%3A%0D%0A{across}%0D%0A%0D%0A"
                  f"Down%3A%0D%0A{down}%0D%0A%0D%0A---%0D%0A%0D%0A"
                  f"Any%20clue%20that%20felt%20unfair%3A%0D%0A%0D%0AName%3A%0D%0A")
    if "was%20it%20useful%20to%20you" not in mailto:
        mailto += ("%0A---%0A%0AThinking%20about%20this%20ICU%20AND%20YOU%20post%20"
                   "overall%20%E2%80%94%20was%20it%20useful%20to%20you%2C%20or%20"
                   "would%20it%20be%20useful%20to%20others%3F%0A")
    return f"""  <div class="pad" style="padding-top:6px">
    <div class="challenge">
      <h2>Sending your answers</h2>
      <p>Finish it, or get as far as you get &mdash; partial sets are welcome and are
        how I find out which clue was unfair.</p>
      <p><a class="btn" href="{mailto}">Send your answers</a></p>
      <p class="fallback">The button opens a reply straight to me with the clue numbers
        already listed. If your device blocks it, write to
        <a href="mailto:icuandyou@icloud.com">icuandyou@icloud.com</a> instead.</p>
    </div>
  </div>
"""


def make_printable(fillable_path):
    src = read(fillable_path)
    out_name = Path(fillable_path).name.replace("-fillable", "")

    geom = extract_geometry(src)
    no = grab(src, r'Superpuzzle #?(\d+)')
    title = grab(src, r'<title>(.*?)</title>')
    h1 = grab(src, r'<h1[^>]*>(.*?)</h1>')
    kicker = grab(src, r'<p class="kicker">(.*?)</p>', required=False, default="")
    desc = grab(src, r'<meta name="description" content="([^"]*)"',
                required=False, default="")
    firstpub = grab(src, r'<span class="firstpub">(.*?)</span>',
                    required=False, default="")
    eyebrow = grab(src, r'<p class="eyebrow">(.*?)</p>')
    footer = grab(src, r'<footer[^>]*>(.*?)</footer>')
    topic_btn = grab(src, r'(<a class="toptopic".*?</a>)', required=False, default="")

    svg, n_cells, n_starts = build_svg(geom, no)
    challenge = build_challenge(src, no, clues_for_challenge(src))
    clues = extract_clues(src)

    # The printable reuses superpuzzle 47's stylesheet, which is the one
    # already designed for a static grid.
    style = grab(read(HERE / "superpuzzle-47-transplantation.html"),
                 r'<style>(.*?)</style>')

    page = f"""<!DOCTYPE html>
<html lang="en-AU">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="alternate icon" href="/favicon.ico" sizes="any">
<link rel="apple-touch-icon" href="/icon-180.png">
<meta name="theme-color" content="#1B2A33">
<meta property="og:site_name" content="ICU AND YOU">
<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="https://icuandyou.com/share-card.png">
<meta name="twitter:card" content="summary_large_image">
<style>{style}{LINK_CSS}</style>
</head>
<body>
<div class="sheet">

  <header class="top">
    <a class="tophome" href="./">&larr;&nbsp; Home</a>
    <a class="topseries" href="./?s=superpuzzle">All superpuzzles</a>
    {topic_btn}
    <p class="eyebrow">{eyebrow}</p>
    <h1>{h1}</h1>
    <p class="kicker">{kicker}</p>
  </header>

  <div class="pad">
    <p class="instruct">The printable version &mdash; grid and clues, nothing to tap.
      Print it, or fill it in with a pen at the desk.</p>
    <div class="gridwrap">{svg}</div>
    <p class="gridnote">On a phone, scroll the grid sideways. It prints cleanly at A4 landscape.</p>
    <div class="links"><a class="printlink"
      href="{Path(fillable_path).name}">Fill it in on screen &nbsp;&rarr;</a></div>
  </div>

  <div class="pad" style="padding-top:0">
    <div class="cols">

{clue_html(clues)}

    </div>
  </div>

{challenge}
  <footer>
    <span class="firstpub">{firstpub}</span>{footer}
  </footer>

</div>
<script data-goatcounter="https://icuandyou.goatcounter.com/count"
        async src="//gc.zgo.at/count.js"></script>
</body>
</html>
"""
    Path(HERE / out_name).write_text(page, encoding="utf-8")
    return out_name, n_cells, n_starts


def add_link_to_fillable(fillable_path, printable_name):
    p = Path(fillable_path)
    s = p.read_text(encoding="utf-8")
    if f'href="{printable_name}"' in s:
        return False                      # already linked
    if "printlink" not in s:              # CSS may already be present
        s = s.replace("</style>", LINK_CSS + "</style>", 1)
    link = PRINT_LINK.format(file=printable_name)
    s2 = re.sub(r'(<p class="(?:gridnote|hint)">.*?</p>)', rf"\1\n    {link}", s,
                count=1, flags=re.S)
    if s2 == s:
        raise SystemExit(f"{p.name}: no gridnote/hint paragraph to anchor the link to")
    p.write_text(s2, encoding="utf-8")
    return True


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--all" in sys.argv:
        args = sorted(str(p) for p in HERE.glob("superpuzzle-*-fillable.html"))
    if not args:
        raise SystemExit(__doc__)

    for f in args:
        name, cells, starts = make_printable(f)
        linked = add_link_to_fillable(f, name)
        print(f"  {name}: {cells} cells, {starts} numbered"
              f"{'  (link added to fillable)' if linked else '  (fillable already linked)'}")


if __name__ == "__main__":
    main()
