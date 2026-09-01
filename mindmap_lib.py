#!/usr/bin/env python3
"""
ICU AND YOU — mind map generator.

Mind maps 29 to 32 were built by a script that no longer exists; this
reconstructs its idiom so future maps are a matter of writing the content,
not placing rectangles. Give it a spec (see build_mindmap_33.py for a
worked example) and it emits the SVG.

Layout, matching the existing series:
    canvas 1120 wide, a curved spine down the centre at x=560
    a header plate at the top with the series line and the title
    stations down the spine, each a coloured pill with an anchor label above
    branch cards either side, 440 wide, connected to the spine by a hairline
    a closing italic line at the foot
"""

W = 1120
MARGIN = 20
CARD_W = 440
SPINE_X = 560
LEFT_X = MARGIN
RIGHT_X = W - MARGIN - CARD_W          # 660

PILL_W, PILL_H = 520, 54
TITLE_DY = 26                          # card top to .ct baseline
FIRST_BULLET_DY = 50                   # card top to first .cb baseline
BULLET_DY = 17.6                       # between bullets
CARD_PAD_BOTTOM = 26

ANCHOR_GAP = 12                        # anchor baseline to pill top
STATION_GAP = 26                       # pill bottom to first card row
ROW_GAP = 30                           # between card rows
AFTER_CARDS = 45                       # last card to next anchor

# The series palette. Each entry: pill/rule colour, card tint, title ink.
PALETTE = {
    "sky":   ("#2E6E8E", "#E7F1F6", "#1E5872"),
    "moss":  ("#4C6B4A", "#EAF1E9", "#3A5539"),
    "rust":  ("#A8442A", "#F9EDE7", "#8A3620"),
    "plum":  ("#6B4570", "#F2ECF3", "#57365B"),
    "slate": ("#4A5560", "#EDF0F2", "#39434D"),
    "gold":  ("#A8721E", "#FBF1DC", "#8A5A14"),
}

SVG_CSS = """
  .ser{font:500 12px 'Helvetica Neue',Arial,sans-serif;letter-spacing:.22em;fill:#7F8B84}
  .ttl{font:400 27px 'Iowan Old Style','Palatino Linotype',Palatino,Georgia,serif;fill:#1B2A33}
  .anch{font:500 11px 'Helvetica Neue',Arial,sans-serif;letter-spacing:.2em}
  .pt{font:500 17px 'Iowan Old Style','Palatino Linotype',Palatino,Georgia,serif;fill:#FCFCFA}
  .ct{font:600 13px 'Helvetica Neue',Arial,sans-serif;letter-spacing:.09em}
  .cb{font:400 12.2px 'Helvetica Neue',Arial,sans-serif;fill:#38424A}
  .bb{font:400 13px 'Helvetica Neue',Arial,sans-serif;fill:#38424A}
  .clos{font:italic 400 14px 'Iowan Old Style','Palatino Linotype',Palatino,Georgia,serif;fill:#6E7570}
"""


def esc(t):
    return (t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace("\u2014", "&#8212;").replace("\u2019", "&#8217;"))


def card_height(bullets):
    return round(FIRST_BULLET_DY + BULLET_DY * (len(bullets) - 1)
                 + CARD_PAD_BOTTOM, 1)


def measure(spec):
    """Walk the spec once to work out the canvas height and every y position."""
    y = 106 + 26                        # below the header plate
    plan = []
    for st in spec["stations"]:
        anchor_y = y
        pill_y = anchor_y + ANCHOR_GAP
        y = pill_y + PILL_H + STATION_GAP

        rows = []
        branches = st["branches"]
        for i in range(0, len(branches), 2):
            pair = branches[i:i + 2]
            h = max(card_height(b["bullets"]) for b in pair)
            rows.append((y, h, pair))
            y += h + ROW_GAP
        y = y - ROW_GAP + AFTER_CARDS
        plan.append(dict(anchor_y=anchor_y, pill_y=pill_y, rows=rows, station=st))
    return plan, y + 40


def spine_path(height, x=SPINE_X, drift=26.0, width=3.0, colour="#7FA0AB", op=0.75):
    """A very slightly drifting vertical line, so it reads as drawn not ruled."""
    top, bottom = 106, height - 44
    pts, n = [], 26
    for i in range(n + 1):
        t = i / n
        yy = top + (bottom - top) * t
        xx = x - drift * (t ** 0.5)
        pts.append(f"{'M' if i == 0 else 'L'}{xx:.1f} {yy:.1f}"
                   if i else f"M{x} {top}")
    return (f'<path d="{" ".join(pts)}" fill="none" stroke="{colour}" '
            f'stroke-width="{width}" opacity="{op}"/>')


def render(spec):
    plan, height = measure(spec)
    o = [f'<svg viewBox="0 0 {W} {height}" xmlns="http://www.w3.org/2000/svg" '
         f'role="img" aria-label="{esc(spec["aria"])}"><style>{SVG_CSS}</style>'
         f'<rect x="0" y="0" width="{W}" height="{height}" fill="#FBFAF7"/>']

    o.append(spine_path(height))
    o.append(spine_path(height, drift=22.0, width=2.4, colour="#9BB6C4", op=0.55))

    # header plate
    o.append(f'<rect x="{MARGIN}" y="16" width="{W - 2*MARGIN}" height="74" '
             f'rx="10" fill="none" stroke="#CFD6D0" stroke-width="0.8"/>')
    o.append(f'<text class="ser" x="{SPINE_X}" y="44" text-anchor="middle">'
             f'{esc(spec["series_line"])}</text>')
    o.append(f'<text class="ttl" x="{SPINE_X}" y="72" text-anchor="middle">'
             f'{esc(spec["title"])}</text>')

    for p in plan:
        st = p["station"]
        rule, tint, ink = PALETTE[st["colour"]]

        # 11px caps with .2em tracking: about 8.3px per character
        aw = len(st["anchor"]) * 8.3 + 22
        o.append(f'<rect x="{SPINE_X - aw/2:.1f}" y="{p["anchor_y"] - 12}" '
                 f'width="{aw:.1f}" height="17" fill="#FBFAF7"/>')
        o.append(f'<text class="anch" x="{SPINE_X}" y="{p["anchor_y"]}" '
                 f'text-anchor="middle" fill="{rule}">{esc(st["anchor"])}</text>')
        o.append(f'<rect x="{(W - PILL_W)//2}" y="{p["pill_y"]}" width="{PILL_W}" '
                 f'height="{PILL_H}" rx="27" fill="{rule}"/>')
        o.append(f'<text class="pt" x="{SPINE_X}" y="{p["pill_y"] + 33}" '
                 f'text-anchor="middle">{esc(st["point"])}</text>')

        for row_y, row_h, pair in p["rows"]:
            for j, br in enumerate(pair):
                x = LEFT_X if j == 0 else RIGHT_X
                o.append(f'<rect x="{x}" y="{row_y}" width="{CARD_W}" '
                         f'height="{row_h}" rx="9" fill="{tint}" '
                         f'stroke="{rule}" stroke-width="0.9"/>')
                o.append(f'<rect x="{x}" y="{row_y}" width="4" height="{row_h}" '
                         f'rx="2" fill="{rule}"/>')
                o.append(f'<text class="ct" x="{x + 18}" y="{row_y + TITLE_DY}" '
                         f'fill="{ink}">{esc(br["title"])}</text>')
                for k, line in enumerate(br["bullets"]):
                    by = round(row_y + FIRST_BULLET_DY + BULLET_DY * k, 1)
                    o.append(f'<text class="cb" x="{x + 18}" y="{by}">'
                             f'{esc(line)}</text>')
                mid = round(row_y + row_h / 2, 1)
                if j == 0:
                    o.append(f'<line x1="{x + CARD_W}" y1="{mid}" x2="{SPINE_X - 8}" '
                             f'y2="{mid}" stroke="{rule}" stroke-width="0.8" '
                             f'opacity="0.42"/>')
                else:
                    o.append(f'<line x1="{SPINE_X + 8}" y1="{mid}" x2="{x}" '
                             f'y2="{mid}" stroke="{rule}" stroke-width="0.8" '
                             f'opacity="0.42"/>')

    o.append(f'<text class="clos" x="{SPINE_X}" y="{height - 22}" '
             f'text-anchor="middle">{esc(spec["closing"])}</text>')
    o.append('</svg>')
    return "".join(o), height
