#!/usr/bin/env python3
"""
ICU AND YOU — index generator.

Rewrites four regions of index.html from page_topic.json:
    THIS WEEK          the week section (topic, blurb, cards)
    PREVIOUS WEEKS     the topic groups
    LATEST             the Latest posts dropdown
    TOPTEN             the Top Ten dropdown

Everything else in index.html — the CSS, the filter menu, the subscribe
strip, the about section, the JavaScript — is left untouched.

The regions are delimited in index.html by marker comments:
    <!-- BUILD:THIS-WEEK -->  ...  <!-- /BUILD:THIS-WEEK -->
Run  python3 build_index.py --insert-markers  once to add them.

Usage:
    python3 build_index.py                 rewrite index.html in place
    python3 build_index.py --check         report what would change, write nothing
    python3 build_index.py --insert-markers
"""

import json
import re
import sys
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent
INDEX = HERE / "index.html"
MANIFEST = HERE / "page_topic.json"

# Order the groups appear in the landing-page menu.
GROUP_ORDER = ["memory", "multimedia", "special", "procedures", "cultural", "other"]


def e(s):
    """Escape for HTML text, matching the quoting style already in index.html."""
    return escape(str(s), quote=True).replace("&#x27;", "&#x27;")


def load():
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def series_sort_key(m, page):
    """Sort pages within a topic by the landing-page menu order, then series."""
    meta = m["series"].get(page["series"])
    if not meta:
        return (99, 99, page["series"])
    _, _, group = meta
    gi = GROUP_ORDER.index(group) if group in GROUP_ORDER else 98
    order = list(m["series"].keys())
    return (gi, order.index(page["series"]), page["series"])


# --------------------------------------------------------------------------
# region builders
# --------------------------------------------------------------------------

def build_this_week(m):
    wk = m["this_week"]
    pages = [p for p in m["pages"] if p.get("week") and not p.get("standing")]
    # "pos" pins the order the cards appear in; a card without one falls
    # back to the landing-page menu order and lands at the end.
    pages.sort(key=lambda p: (p.get("pos", 999), series_sort_key(m, p)))

    out = [
        f'  <section class="week" id="week" data-topic="{e(wk["topic"])}" '
        f'data-slug="{wk["slug"]}">',
        '    <p class="wk-k">This week</p>',
        f'    <h2 class="wk-t">{e(wk["topic"])}</h2>',
        f'    <p class="wk-b">{e(wk["blurb"])}</p>',
        '    <ul class="list">',
    ]
    for p in pages:
        badge = p.get("badge") or m["series"][p["series"]][0]
        series_attr = " ".join([p["series"]] + p.get("guests", []))
        num = f'<b>{e(p["number"])}</b>' if p.get("number") else ""
        link = p.get("link_label") or "Open"
        out += [
            f'        <li class="item {p["colour"]}" data-series="{series_attr}">',
            f'          <div class="badge">{e(badge)}{num}</div>',
            '          <div class="body">',
            f'            <h3>{e(p["title"])}</h3>',
            f'            <p>{e(p.get("blurb", ""))}</p>',
            f'            <div class="links"><a class="go" href="{p["file"]}">{e(link)}</a></div>',
            '          </div>',
            '        </li>',
        ]
    out += ['    </ul>', '  </section>']
    return "\n".join(out)


def build_previous(m):
    """Topic groups, most recent topic first, then a group for the standing
    series. Some pieces — a book review, a procedure, the Top Ten — belong to
    the site rather than to a fortnight, and filing them under whichever topic
    happened to be running when they went up is simply wrong. They carry
    "standing": true in the manifest and collect here instead."""
    order, seen = [], set()
    for p in m["pages"]:
        if p.get("standing"):
            continue
        if not p.get("week") and p["slug"] not in seen:
            seen.add(p["slug"])
            order.append((p["slug"], p["topic"]))

    out = []
    for slug, topic in order:
        pages = [p for p in m["pages"]
                 if p["slug"] == slug and not p.get("week") and not p.get("standing")]
        pages.sort(key=lambda p: series_sort_key(m, p))

        dots = "".join(
            f'<i class="dot {p["colour"]}" title="{e(m["series"][p["series"]][0])}"></i>'
            for p in pages
        )
        n = len(pages)
        out += [
            f'      <details class="group" data-topic="{e(topic)}" data-slug="{slug}">',
            '        <summary>',
            f'          <span class="tname">{e(topic)}</span>',
            f'          <span class="tdots">{dots}</span>',
            f'          <span class="tcount">{n} piece{"s" if n != 1 else ""}</span>',
            '        </summary>',
            '        <ul class="rows">',
        ]
        for p in pages:
            label = m["series"][p["series"]][0]
            series_attr = " ".join([p["series"]] + p.get("guests", []))
            out.append(
                f'            <li class="row {p["colour"]}" data-series="{series_attr}">'
                f'<span class="rs">{e(label)}</span>'
                f'<span class="rn">{e(p.get("number") or "")}</span>'
                f'<a class="rt" href="{p["file"]}">{e(p["title"])}</a></li>'
            )
        out += ['        </ul>', '      </details>']

    standing = [p for p in m["pages"] if p.get("standing")]
    if standing:
        standing.sort(key=lambda p: (series_sort_key(m, p), int(p.get("number") or 0)))
        # One dot per series here, not per piece: this group grows by series
        # over time, and twelve identical dots would say nothing.
        seen_series = []
        for p in standing:
            if p["series"] not in seen_series:
                seen_series.append(p["series"])
        dots = "".join(
            f'<i class="dot {m["series"][k][1]}" title="{e(m["series"][k][0])}"></i>'
            for k in seen_series)
        n = len(standing)
        out += [
            '      <details class="group" data-topic="Any time" data-slug="standing">',
            '        <summary>',
            '          <span class="tname">Any time \u2014 not tied to a fortnight</span>',
            f'          <span class="tdots">{dots}</span>',
            f'          <span class="tcount">{n} piece{"s" if n != 1 else ""}</span>',
            '        </summary>',
            '        <ul class="rows">',
        ]
        for p in standing:
            label = m["series"][p["series"]][0]
            series_attr = " ".join([p["series"]] + p.get("guests", []))
            out.append(
                f'            <li class="row {p["colour"]}" data-series="{series_attr}">'
                f'<span class="rs">{e(label)}</span>'
                f'<span class="rn">{e(p.get("number") or "")}</span>'
                f'<a class="rt" href="{p["file"]}">{e(p["title"])}</a></li>')
        out += ['        </ul>', '      </details>']
    return "\n".join(out)


def build_latest(m):
    out = ['        <div class="menu">']
    for x in m["latest"]:
        out.append(
            f'          <a class="mi newitem" href="{x["file"]}">'
            f'<span class="newtag">New</span>'
            f'<i class="md {x["colour"]}"></i>{e(x["label"])}</a>'
        )
    out.append('        </div>')
    return "\n".join(out)


def build_topten(m):
    out = ['        <div class="menu">']
    for x in m["topten"]:
        out.append(
            f'          <a class="mi newitem" href="{x["file"]}">'
            f'<i class="md {x["colour"]}"></i>{e(x["label"])}</a>'
        )
    out.append('        </div>')
    return "\n".join(out)


def build_teaser(m):
    """The 'Coming next' strip. Hand-edited until Aug 2026, and the thing most
    likely to go stale; generated from the manifest now."""
    t = m.get("teaser")
    if not t:
        return '      <p class="teaser"></p>'
    out = ['      <p class="teaser">',
           f'        <span class="tz">{e(t["label"])}</span>']
    for ln in t["lines"]:
        # "tt" is the large line — the topic. "tm" is the quieter one.
        # Emphasis follows the kind of event, not the position in the list,
        # so the lines stay in date order whatever is coming next.
        cls = "tt" if ln.get("emphasis") else "tm"
        out.append(f'        <span class="{cls}"><b>{e(ln["date"])}</b> '
                   f'&nbsp;&mdash;&nbsp; {e(ln["what"])}</span>')
    out.append('      </p>')
    return "\n".join(out)


def build_procedures(m):
    """The Procedures menu. Unlike the other groups this one is a reference
    shelf — readers arrive wanting a named procedure, not a stream — so it
    lists the pages themselves under the filter. It was hand-maintained until
    September 2026, drifted, and stopped listing anything published after the
    first entry. Generated now."""
    pages = sorted((p for p in m["pages"] if p["series"] == "procedures"),
                   key=lambda p: int(p.get("number") or 0))
    out = ['        <div class="menu">',
           '          <button class="mi" data-f="procedures">'
           '<i class="md amethyst"></i>All procedures</button>']
    for p in pages:
        out.append(f'          <a class="mi" href="{p["file"]}">'
                   f'<i class="md amethyst"></i>{e(p["title"])}</a>')
    out.append('        </div>')
    return "\n".join(out)


REGIONS = {
    "TEASER": build_teaser,
    "PROCEDURES": build_procedures,
    "THIS-WEEK": build_this_week,
    "PREVIOUS-WEEKS": build_previous,
    "LATEST": build_latest,
    "TOPTEN": build_topten,
}


# --------------------------------------------------------------------------
# marker insertion (one-off)
# --------------------------------------------------------------------------

def insert_markers(src):
    """Wrap the four existing regions in marker comments. Idempotent."""
    def wrap(src, name, pattern):
        if f"BUILD:{name}" in src:
            print(f"  {name}: markers already present")
            return src
        mm = re.search(pattern, src, re.S)
        if not mm:
            print(f"  {name}: PATTERN NOT FOUND — insert by hand")
            return src
        body = mm.group(0)
        src = src.replace(
            body, f"<!-- BUILD:{name} -->\n{body}\n<!-- /BUILD:{name} -->", 1
        )
        print(f"  {name}: wrapped ({len(body)} bytes)")
        return src

    src = wrap(src, "TEASER", r'      <p class="teaser">.*?</p>')
    src = wrap(src, "PROCEDURES",
               r'(?<=<details class="drop" data-g="procedures">\n'
               r'        <summary class="chip grp">Procedures</summary>\n)'
               r'        <div class="menu">.*?</div>')
    src = wrap(src, "THIS-WEEK", r'  <section class="week".*?</section>')
    src = wrap(src, "PREVIOUS-WEEKS",
               r'      <details class="group".*</details>(?=\s*\n\s*<p class="empty")')
    src = wrap(src, "LATEST",
               r'(?<=<details class="drop latest" id="latest">\n'
               r'        <summary class="chip newbtn">Latest posts</summary>\n)'
               r'        <div class="menu">.*?</div>')
    src = wrap(src, "TOPTEN",
               r'(?<=<details class="drop topten" id="topten">\n'
               r'        <summary class="chip topbtn">The Top Ten</summary>\n)'
               r'        <div class="menu">.*?</div>')
    return src


# --------------------------------------------------------------------------

def main():
    args = sys.argv[1:]
    src = INDEX.read_text(encoding="utf-8")

    if "--insert-markers" in args:
        print("Inserting build markers into index.html")
        out = insert_markers(src)
        INDEX.write_text(out, encoding="utf-8")
        print("Done. Commit this, then build_index.py can run normally.")
        return

    m = load()
    missing = [n for n in REGIONS if f"<!-- BUILD:{n} -->" not in src]
    if missing:
        sys.exit(f"index.html has no markers for: {', '.join(missing)}\n"
                 f"Run:  python3 build_index.py --insert-markers")

    changed = []
    for name, fn in REGIONS.items():
        pat = re.compile(
            f"(<!-- BUILD:{name} -->\n).*?(\n<!-- /BUILD:{name} -->)", re.S
        )
        new_body = fn(m)
        old = pat.search(src).group(0)
        new = f"<!-- BUILD:{name} -->\n{new_body}\n<!-- /BUILD:{name} -->"
        if old != new:
            changed.append(name)
        src = pat.sub(lambda _: new, src, count=1)

    if "--check" in args:
        print("would change:", ", ".join(changed) if changed else "nothing")
        return

    INDEX.write_text(src, encoding="utf-8")
    n_week = sum(1 for p in m["pages"] if p.get("week"))
    n_prev = sum(1 for p in m["pages"] if not p.get("week"))
    print(f"index.html rebuilt — this week: {n_week}, previous: {n_prev}, "
          f"latest: {len(m['latest'])}, top ten: {len(m['topten'])}")
    print("regions changed:", ", ".join(changed) if changed else "none")


if __name__ == "__main__":
    main()
