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
            "corrections.html", "you-asked.html", "on-your-phone.html"}

# Pages that deliberately carry no reply-email line.
NO_REPLY_LINE = {"about.html", "corrections.html", "you-asked.html",
                 "on-your-phone.html"}

# Pages that deliberately carry no subscribe footer line.
# (Site-wide pages don't sell the newsletter — set by Michael, Aug 2026.)
NO_SUBSCRIBE_LINE = {"about.html", "corrections.html", "glossary.html",
                     "you-asked.html", "on-your-phone.html"}

# Some series are not tied to a topic and so have no topic to link to:
# the Top Ten spans topics by design, and a book review belongs to the
# reader rather than to an age group.
# Pieces with no topic to link to: the Top Ten spans topics, a book belongs to
# the reader, procedures are standing, and the general-public series deliberately
# does not send a lay reader into the clinical archive for that topic.
NO_TOPIC_BUTTON_PREFIX = ("top-ten-", "book-club-", "procedures-", "public-", "exam-")

SUBSCRIBE = "Two emails a week"
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
    # A standing piece belongs to no fortnight, so it has no topic to link to.
    standing = {p["file"]: True for p in (m or {}).get("pages", []) if p.get("standing")}
    for f in content:
        s = (HERE / f).read_text(encoding="utf-8")
        for label, test in CHECKS:
            if label == "topic button" and (
                    f.startswith(NO_TOPIC_BUTTON_PREFIX) or standing.get(f)):
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

    # ---- ?s= and ?g= links must resolve to a filter on the landing page ----
    filters = set(re.findall(r'data-f="([^"]+)"', index))
    for f in html_files:
        src = (HERE / f).read_text(encoding="utf-8")
        for key in set(re.findall(r'\?s=([a-z0-9-]+)', src)):
            if key not in filters:
                problems.append(f"{f}: links to ?s={key}, which matches no filter "
                                f"on the landing page \u2014 it will land on the "
                                f"unfiltered index")
        for key in set(re.findall(r'\?g=([a-z0-9-]+)', src)):
            if f"g:{key}" not in filters:
                problems.append(f"{f}: links to ?g={key}, which matches no group filter")

    # ---- a page must agree with itself ------------------------------------
    # Every page here is built by copying the last one in its series, and the
    # bits nobody re-reads are the footer line and the body of the reply
    # email. Mnemonic 57 shipped with "Mnemonic No. 56 ... The School-Age
    # Child" in its footer; superquizzes 62 and 63 both opened their result
    # email "ICU Superquiz #6N — The postneonatal infant", inherited from 61
    # and carried forward twice. Grepping for the old topic missed all three,
    # because the stale text used a different spelling each time.
    #
    # So compare the page against itself and against its own manifest entry
    # rather than searching for whatever is expected to be wrong.
    series_label = {k: v[0] for k, v in m.get("series", {}).items()}
    topic_names = {p.get("topic") for p in m["pages"] if p.get("topic")}
    by_file = {p["file"]: p for p in m["pages"]}

    for f in content:
        p = by_file.get(f)
        if not p:
            continue
        s = (HERE / f).read_text(encoding="utf-8")
        label, num = series_label.get(p.get("series")), p.get("number")

        # 1. Every time a page names its own series and a number, it must be
        #    this page's number.
        if label and num:
            pat = re.escape(label) + r"\s*(?:&nbsp;)?\s*(?:No\.|Number|#)\s*(\d+)"
            wrong = {n for n in re.findall(pat, s, re.I) if n != str(num)}
            if wrong:
                problems.append(
                    f"{f}: calls itself {label} #{', #'.join(sorted(wrong))} somewhere, "
                    f"but the manifest says #{num} — usually a footer or an email "
                    f"body carried over from the previous piece")

        # 2. The topic button must point at this page's own topic.
        if not f.startswith(NO_TOPIC_BUTTON_PREFIX):
            for slug in set(re.findall(r'\?t=([a-z0-9-]+)', s)):
                if p.get("slug") and slug != p["slug"]:
                    problems.append(
                        f'{f}: links to ?t={slug} but the manifest puts it under '
                        f'"{p["slug"]}"')

        # 3. A reply email is about the page it sits on, so any topic named in
        #    one must be this page's topic. This is the check that catches a
        #    mail body inherited from a different block.
        mail = " ".join(re.findall(r'mailto:[^"\']+', s)
                        + re.findall(r'var body\s*=\s*(.*?);\s*\n', s, re.S))
        if mail and p.get("topic"):
            for t in topic_names:
                if t != p["topic"] and t.lower() in mail.lower():
                    problems.append(
                        f'{f}: its reply email names "{t}", but the page is filed '
                        f'under "{p["topic"]}"')

    # ---- the week heading must match the pages under it -------------------
    # The "this_week" block in the manifest supplies the heading, slug and
    # preamble; the pages are flagged individually with "week": true. Rolling
    # a block over means changing both, and in September 2026 only one was
    # changed \u2014 so the landing page announced the wrong topic for a day.
    wk = m.get("this_week", {})
    week_slugs = {p["slug"] for p in m["pages"]
                  if p.get("week") and not p.get("standing")}
    if week_slugs and wk.get("slug") not in week_slugs:
        problems.append(
            f'page_topic.json: this_week.slug is "{wk.get("slug")}" but the pages '
            f'flagged for this week are {sorted(week_slugs)} \u2014 the landing page '
            f'heading will not match its own cards')
    if len(week_slugs) > 1:
        problems.append(
            f"page_topic.json: pages from more than one topic are flagged "
            f"week=true: {sorted(week_slugs)}")

    # ---- this week's pages must appear in Latest posts --------------------
    # Everything else about a new piece follows from the manifest: the card,
    # the topic group, the series menu, the topic index, the counts. Latest
    # posts does not — it is a hand-set list, so a page can go up complete in
    # every other respect and still be missing from the one control a returning
    # reader actually looks at. That happened in September 2026 and the reader
    # found it before the audit did.
    # New pages are appended, so the tail of "pages" is the order they went up,
    # and the newest few should be exactly what "latest" holds. Comparing the
    # tail rather than the whole fortnight keeps this quiet: a block runs to
    # twenty pieces and the control holds five, so "every page of this week"
    # would cry wolf fifteen times. If a page is ever inserted into the middle
    # of "pages" rather than appended, this check will misread which are newest.
    listed = {x["file"] for x in m.get("latest", [])}
    n_slots = len(m.get("latest", []))
    newest = m["pages"][-n_slots:] if n_slots else []
    for p in newest:
        if p["file"] in listed:
            continue
        label = m["series"][p["series"]][0]
        num = f' {p["number"]}' if p.get("number") else ""
        problems.append(
            f'page_topic.json: {p["file"]} is one of the {n_slots} most recently '
            f'added pages but is not in "latest" — it will not appear under '
            f'Latest posts. Add, at the top:  '
            f'{{"file": "{p["file"]}", "colour": "{p["colour"]}", '
            f'"label": "{label}{num} · {p["title"]}"}}')

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
