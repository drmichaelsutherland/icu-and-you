#!/usr/bin/env python3
"""
ICU AND YOU — weekly structural audit.

Run as the last step before upload. Checks every page for the things that
should be on it, checks the manifest against what is actually on disk, and
prints the Latest posts list so the Friday housekeeping is a copy rather
than a memory test.

    python3 audit.py            full report
    python3 audit.py --quiet    problems only (exit 1 if any)
"""

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Site-wide pages: not content, exempt from the content-page checks.
SITEWIDE = {"index.html", "about.html", "glossary.html",
            "corrections.html", "you-asked.html"}

# Pages that deliberately carry no reply-email line.
NO_REPLY_LINE = {"about.html", "corrections.html", "you-asked.html"}

# Pages that deliberately carry no subscribe footer line.
# (Site-wide pages don't sell the newsletter — set by Michael, Aug 2026.)
NO_SUBSCRIBE_LINE = {"about.html", "corrections.html", "glossary.html",
                     "you-asked.html"}

# The Top Ten spans topics by design, so it has no single topic to link to.
NO_TOPIC_BUTTON_PREFIX = "top-ten-"

SUBSCRIBE = "One email on Fridays"
REPLY_LINE = "was%20it%20useful%20to%20you"
REPLY_LINE_PLAIN = "was it useful to you"

CHECKS = [
    ("lang en-AU",      lambda s: '<html lang="en-AU"' in s),
    ("meta description", lambda s: '<meta name="description"' in s),
    ("favicon svg",     lambda s: 'href="/favicon.svg"' in s),
    ("apple touch icon", lambda s: 'href="/icon-180.png"' in s),
    ("theme-color",     lambda s: '<meta name="theme-color"' in s),
    ("og:title",        lambda s: 'property="og:title"' in s),
    ("og:image",        lambda s: 'property="og:image"' in s),
    ("twitter:card",    lambda s: 'name="twitter:card"' in s),
    ("home button",     lambda s: 'class="tophome"' in s),
    ("series button",   lambda s: 'class="topseries"' in s),
    ("topic button",    lambda s: 'class="toptopic"' in s),
    ("linked masthead", lambda s: 'class="mast"' in s),
    ("first published", lambda s: 'class="firstpub"' in s),
    ("goatcounter",     lambda s: 'goatcounter' in s),
]


def load_manifest():
    p = HERE / "page_topic.json"
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def main():
    quiet = "--quiet" in sys.argv
    problems = []
    notes = []

    html_files = sorted(p.name for p in HERE.glob("*.html"))
    index = (HERE / "index.html").read_text(encoding="utf-8")
    m = load_manifest()

    # ---- per-page structural checks -------------------------------------
    content = [f for f in html_files if f not in SITEWIDE]
    for f in content:
        s = (HERE / f).read_text(encoding="utf-8")
        for label, test in CHECKS:
            if label == "topic button" and f.startswith(NO_TOPIC_BUTTON_PREFIX):
                continue
            if not test(s):
                problems.append(f"{f}: missing {label}")
        if f not in NO_SUBSCRIBE_LINE and SUBSCRIBE not in s:
            problems.append(f"{f}: missing subscribe footer line")
        if f not in NO_REPLY_LINE and REPLY_LINE not in s \
                and REPLY_LINE_PLAIN not in s:
            problems.append(f"{f}: missing usefulness line in reply email")

    # site-wide pages get the light check only
    for f in sorted(SITEWIDE & set(html_files)):
        s = (HERE / f).read_text(encoding="utf-8")
        for label in ("favicon svg", "goatcounter"):
            test = dict(CHECKS)[label]
            if not test(s):
                problems.append(f"{f}: missing {label}")

    # ---- orphans: live pages nothing links to ---------------------------
    linked = set(re.findall(r'href="([\w./-]+\.html)"', index))
    for f in html_files:
        if f in SITEWIDE or f in linked:
            continue
        # a page linked from any other page is not an orphan
        if any(f in (HERE / o).read_text(encoding="utf-8")
               for o in html_files if o != f):
            continue
        problems.append(f"{f}: ORPHAN — live on the site, linked from nowhere")

    # ---- manifest vs disk ------------------------------------------------
    if m:
        for p in m["pages"]:
            if not (HERE / p["file"]).exists():
                problems.append(f'{p["file"]}: in manifest, not on disk')
        known = {p["file"] for p in m["pages"]}
        for f in content:
            if f not in known and not f.startswith("top-ten-"):
                notes.append(f"{f}: on disk, not in the manifest")

        # ---- dead links --------------------------------------------------
        for f in html_files:
            s = (HERE / f).read_text(encoding="utf-8")
            for href in set(re.findall(r'href="([\w-]+\.html)"', s)):
                if not (HERE / href).exists():
                    problems.append(f"{f}: dead link to {href}")

    # ---- Friday housekeeping output --------------------------------------
    if m and not quiet:
        wk = m["this_week"]
        print(f"\n  THIS WEEK: {wk['topic']}  ({wk['slug']})")
        week_pages = sorted((p for p in m["pages"] if p.get("week")),
                            key=lambda p: p.get("pos", 999))
        for p in week_pages:
            n = f" #{p['number']}" if p.get("number") else ""
            print(f"    {m['series'][p['series']][0]}{n} — {p['title']}")

        print("\n  LATEST POSTS (paste into the dropdown, newest first):")
        for x in m["latest"]:
            print(f'    <a class="mi newitem" href="{x["file"]}">'
                  f'<span class="newtag">New</span>'
                  f'<i class="md {x["colour"]}"></i>{x["label"]}</a>')

        topics = {}
        for p in m["pages"]:
            topics.setdefault(p["topic"], []).append(p)
        print(f"\n  {len(m['pages'])} pieces across {len(topics)} topics:")
        for t, ps in topics.items():
            print(f"    {t}: {len(ps)}")

    # ---- superpuzzle grids: declared tracks must match the cells --------
    for f in [x for x in html_files if x.startswith("superpuzzle-")
              and x.endswith("-fillable.html")]:
        src = (HERE / f).read_text(encoding="utf-8")
        cols = re.search(r"grid-template-columns:repeat\((\d+)", src)
        rows = re.search(r"grid-template-rows:repeat\((\d+)", src)
        placed = re.findall(r"grid-column:(\d+);grid-row:(\d+)", src)
        if not (cols and rows and placed):
            continue
        mx = max(int(c) for c, _ in placed)
        my = max(int(r) for _, r in placed)
        if mx != int(cols.group(1)) or my != int(rows.group(1)):
            problems.append(
                f"{f}: grid declares {cols.group(1)}x{rows.group(1)} tracks but "
                f"cells need {mx}x{my} \u2014 cells will stretch or phantom rows appear")

    # ---- glossary links: must resolve, and the card script must be loaded ----
    gl_src = (HERE / "glossary.js")
    if gl_src.exists():
        ids = set(re.findall(r'"([a-z0-9-]+)": \{"t"', gl_src.read_text(encoding="utf-8")))
        for f in content:
            src = (HERE / f).read_text(encoding="utf-8")
            used = set(re.findall(r'glossary\.html#([a-z0-9-]+)', src))
            dead = used - ids
            if dead:
                problems.append(f"{f}: glossary link(s) with no entry: {', '.join(sorted(dead))}")
            if 'class="gl"' in src and 'glossary.js' not in src:
                problems.append(f"{f}: uses glossary links but does not load glossary.js")

    # ---- report -----------------------------------------------------------
    print()
    if notes and not quiet:
        for n in notes:
            print(f"  note     {n}")
        print()
    if problems:
        for p in problems:
            print(f"  PROBLEM  {p}")
        print(f"\n  {len(problems)} problem(s) across {len(html_files)} pages.")
        sys.exit(1)
    print(f"  Audit clean — {len(html_files)} pages, "
          f"{len(content)} of them content pages.")


if __name__ == "__main__":
    main()
