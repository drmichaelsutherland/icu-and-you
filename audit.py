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

import hashlib
import json
import re
import sys
from collections import defaultdict
from html import unescape
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

    # ---- a page that asks for a reply must say how credit works ----------
    # Agreed October 2026, after a survey found 54 of 88 pages with a reply
    # box said nothing at all about what happens to a contributor's name,
    # and the 34 that did say something said it eleven different ways —
    # usually covering only the case where the reader writes the piece, so
    # somebody who merely sent in a paper or an answer was told nothing.
    # One sentence now, identical everywhere, as standard furniture in the
    # box. This check exists so the next new page cannot quietly omit it.
    # Widened October 2026. The first version looked only for class="challenge"
    # and class="reply", so it had never once examined the seven aphorism pages,
    # which use class="reflect". That is why Aphorism 40 passed clean when it was
    # built and was in fact missing the line — it was built from Aphorism 39,
    # which did not have one either. class="picks" is checked here too for
    # completeness, though every mnemonic page carrying it also carries a
    # challenge box, so it adds nothing today and may not always.
    CREDIT = "How you are credited is entirely your call"
    BOXES = ('challenge', 'reply', 'reflect', 'picks')
    for f in content:
        s = (HERE / f).read_text(encoding="utf-8")
        if not any('class="%s"' % c in s for c in BOXES):
            continue
        n = s.count(CREDIT)
        if n == 0:
            problems.append(f"{f}: has a reply box but no credit line — a reader "
                            f"is being asked to send something without being told "
                            f"whether their name goes on it")
        elif n > 1:
            problems.append(f"{f}: the credit line appears {n} times")

    # ---- scaffolding left in a finished page ------------------------------
    # The cheapest possible check, and worth having. Pages here get built in
    # stages — the prose first, the source line or a figure filled in once it
    # has been verified — and a placeholder is by definition something that
    # looked fine at the moment it was typed. Anything in this list is a
    # sentence nobody meant a reader to see.
    # Matched case-sensitively on purpose. Scaffolding is written in capitals
    # and real prose is not: the India Room page says its own name "is a
    # placeholder" and every quiz has an input with placeholder="Type your
    # name", and neither is a defect.
    SHOUTED = ("PLACEHOLDER", "TODO", "TK TK", "FIXME", "XXXX", "TBC", "TBD")
    QUIET = ("lorem ipsum", "[insert ", "[add ")
    for f in content:
        s = (HERE / f).read_text(encoding="utf-8")
        body = re.sub(r"<script.*?</script>|<!--.*?-->", "", s, flags=re.S)
        for tag in SHOUTED:
            if tag in body:
                problems.append(f'{f}: still contains "{tag}" — scaffolding left '
                                f"in a page that is otherwise finished")
        for tag in QUIET:
            if tag in body.lower():
                problems.append(f'{f}: still contains "{tag}" — scaffolding left '
                                f"in a page that is otherwise finished")

    # ---- a class used in the markup must be styled somewhere in the page --
    # Found October 2026: twelve pages — the whole Multimedia group — used
    # class="btn" for the reply button and never defined .btn, so the button
    # that is the entire point of a challenge box rendered as a plain blue
    # underlined link. Nothing else caught it, because each page was valid,
    # linked correctly and read correctly; only looking at it showed the
    # problem, and nobody looks at a page they wrote six weeks ago.
    #
    # Same principle as the other checks here: compare the page against
    # itself. A class in a class="" attribute with no mention anywhere in the
    # page's own <style> block is either dead markup or an unstyled element.
    # Matching the bare name rather than a full selector keeps this quiet for
    # classes styled by descent (.challenge h2) or in a media query.
    #
    # .btn is a problem because a dead reply button costs replies. The rest
    # are notes, because some are legitimately styled elsewhere and the point
    # is to put the list in front of a human each Friday, not to block.
    STYLED_ELSEWHERE = {
        "gl", "gl-card",            # glossary.js injects its own rules
        "segno", "qrimg", "qrline",  # QR markup; the SVG carries its own attrs
        "ct", "ot",                  # puzzle SVG text, styled by attribute
    }
    unstyled = {}
    for f in content:
        s = (HERE / f).read_text(encoding="utf-8")
        style = "\n".join(re.findall(r"<style>(.*?)</style>", s, re.S))
        if not style:
            continue
        markup = re.sub(r"<style>.*?</style>", "", s, flags=re.S)
        used = set()
        for attr in re.findall(r'class="([^"]*)"', markup):
            used |= set(attr.split())
        for cls in sorted(used - STYLED_ELSEWHERE):
            if re.search(r"[.\s]" + re.escape(cls) + r"\b", style):
                continue
            if cls == "btn":
                problems.append(
                    f'{f}: uses class="btn" but never defines .btn — the reply '
                    f"button will render as a plain underlined link")
            else:
                unstyled.setdefault(cls, []).append(f)
    for cls, fs in sorted(unstyled.items(), key=lambda kv: -len(kv[1])):
        shown = ", ".join(fs[:3]) + (f" and {len(fs) - 3} more" if len(fs) > 3 else "")
        notes.append(f'class "{cls}" is used but never styled, on {len(fs)} '
                     f"page{'s' if len(fs) > 1 else ''}: {shown}")

    # ---- prose inherited from the page a new page was built from ----------
    # October 2026, and the reason this check exists: Mind Map 36 went out
    # with Mind Map 35's entire opening — lede and two paragraphs, word for
    # word, about adolescents. Every other check passed, because nothing was
    # broken. The page was valid, linked correctly, rendered correctly and
    # was about the wrong patient. Michael found it by reading it.
    #
    # Every page here is built from an earlier one, so this will happen again.
    # The discriminator is how many pages a block appears on: the subscribe
    # line and the series explainers are furniture and appear on dozens; a
    # paragraph of body prose on exactly two or three pages was copied and
    # forgotten.
    #
    # Today's intentional sharing is recorded in prose_baseline.json by its
    # hash, not by which pages carry it, so adding Bare Bones 3 does not
    # re-trigger the Bare Bones explainer. Anything NOT in that file is new,
    # and new shared prose is the bug. If it turns out to be deliberate, the
    # fix is to paste the printed line into the baseline.
    # The footer is the second place this happens, and the first version of
    # this check could not see it. Mind Map 36 went up carrying Mind Map 35's
    # source line — the ANZPIC registry, the Immunisation Handbook and
    # anaphylaxis series, on a page about eighteen to thirty year olds — because
    # that line is bare text between <br> tags inside <footer> rather than a
    # <p> or an <li>, so nothing below was looking at it. Footer prose is now
    # collected too: split the footer on its line breaks and judge each chunk
    # on the same thresholds. The subscribe line and the standing disclaimer
    # appear on every page and so fall out as furniture by themselves.
    MIN_WORDS, FURNITURE_AT = 14, 6
    seen = defaultdict(set)
    for f in content:
        s = (HERE / f).read_text(encoding="utf-8")
        s = re.sub(r"<style>.*?</style>|<script.*?</script>|<svg.*?</svg>|<!--.*?-->",
                   "", s, flags=re.S)
        blocks = [c[0] or c[1] for c in
                  re.findall(r"<p\b[^>]*>(.*?)</p>|<li\b[^>]*>(.*?)</li>", s, re.S)]
        foot = re.search(r"<footer\b[^>]*>(.*?)</footer>", s, re.S)
        if foot:
            body = re.sub(r"<p\b[^>]*>.*?</p>", "", foot.group(1), flags=re.S)
            blocks += re.split(r"<br\s*/?>", body)
        for c in blocks:
            t = re.sub(r"<[^>]+>", " ", c)
            t = re.sub(r"&[a-z]+;|&#\d+;", " ", t)
            t = re.sub(r"\s+", " ", t).strip()
            if len(t.split()) >= MIN_WORDS:
                seen[t].add(f)

    bl_path = HERE / "prose_baseline.json"
    try:
        baseline = json.loads(bl_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        baseline = {}
        notes.append("prose_baseline.json is missing — the inherited-prose check "
                     "cannot tell new sharing from old, so it is passing everything")

    # A companion page is the same piece in another format — the printable and
    # fillable superpuzzles are generated from each other, and a procedure's
    # checklist is a cut-down of its long version. Identical text across those
    # is the point, so collapse them to one stem before judging.
    def stem(f):
        return re.sub(r"-(fillable|printable|checklist)\.html$", ".html", f)

    for t, ps in sorted(seen.items(), key=lambda kv: -len(kv[1])):
        if not (2 <= len(ps) < FURNITURE_AT):
            continue
        if len({stem(p) for p in ps}) == 1:
            continue
        h = hashlib.sha1(t.encode()).hexdigest()[:16]
        if h in baseline:
            continue
        problems.append(
            f"inherited prose: {len(t.split())} words appear on "
            f"{' and '.join(sorted(ps))} — if that is a page built from another "
            f"and not rewritten, fix the page; if it is deliberate, add to "
            f'prose_baseline.json:  "{h}": {{"note": "...", '
            f'"opening": "{" ".join(t.split()[:9])}…"}}\n'
            f"             “{t[:120]}…”")

    # ---- a page's script must agree with the page's own markup ----------
    # October 2026, and this one would have shipped. Mnemonic 58 was built
    # from Mnemonic 57, which drives its answer picker from a JavaScript
    # array of the options. The markup was rewritten with the new six; the
    # array was not. Choosing "L - Lipids" displayed "A - Adult body, adult
    # doses", and that is what the reply email would have carried, so every
    # response would have been about the wrong piece.
    #
    # Nothing structural saw it. The HTML was valid, the letters rendered,
    # the links resolved, the audit passed. It showed up only on clicking a
    # radio button and reading what came back.
    #
    # Same family as the inherited-prose check above, but for behaviour
    # rather than text: where a page states its options twice, the two
    # statements must match. Compared on the visible label, since the array
    # holds plain text and the markup holds entities.
    for f in content:
        s = (HERE / f).read_text(encoding="utf-8")
        arr = re.search(r'var ITEMS = (\[.*?\]);', s, re.S)
        if not arr:
            continue
        try:
            items = json.loads(arr.group(1))
        except json.JSONDecodeError:
            problems.append(f"{f}: the ITEMS array in its script is not valid JSON")
            continue
        labels = re.findall(r'<span class="cl">(.*?)</span>\s*<span class="pt">(.*?)</span>', s, re.S)
        if not labels:
            problems.append(f"{f}: has an ITEMS array but no options in the markup for it to drive")
            continue
        if len(labels) != len(items):
            problems.append(
                f"{f}: {len(labels)} options in the markup but {len(items)} in the script's "
                f"ITEMS array — the reply will report the wrong one")
            continue
        for i, ((cl, pt), it) in enumerate(zip(labels, items)):
            want = (unescape(cl).strip(), re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", "", pt))).strip())
            got = (str(it.get("l", "")).strip(), re.sub(r"\s+", " ", str(it.get("t", ""))).strip())
            if want != got:
                problems.append(
                    f"{f}: option {i + 1} is {want[0]!r} / {want[1]!r} in the markup but "
                    f"{got[0]!r} / {got[1]!r} in the script — a reader choosing it would "
                    f"send the wrong answer")

    # ---- the GROUPS map must know every series --------------------------
    # The landing page carries the series-to-group map twice: once as the
    # buttons in the menu, and once as a JavaScript object the "All of ..."
    # filters read. Adding a series touches the first and it is easy to
    # forget the second, at which point the series still has its own button
    # and quietly vanishes from its group's "All" filter. That had happened
    # to three of them -- A View from England, Historical Snapshots and
    # Notable Doctors -- before this check existed.
    gm = re.search(r'var GROUPS = (\{.*?\});', index, re.S)
    if not gm:
        problems.append("index.html: GROUPS map not found")
    else:
        try:
            groups = json.loads(gm.group(1))
        except ValueError as exc:
            problems.append(f"index.html: GROUPS map is not valid JSON ({exc})")
            groups = None
        if groups is not None:
            declared = {k: v[2] for k, v in m.get("series", {}).items()
                        if len(v) > 2}
            for series, group in sorted(declared.items()):
                if group not in groups:
                    problems.append(f"index.html: series {series!r} is in group "
                                    f"{group!r}, which is not in the GROUPS map")
                elif series not in groups[group]:
                    problems.append(f"index.html: series {series!r} is missing "
                                    f"from GROUPS[{group!r}] — it will not "
                                    f"appear under “All” for that group")
            for group, members in sorted(groups.items()):
                for series in members:
                    if series not in declared:
                        problems.append(f"index.html: GROUPS[{group!r}] lists "
                                        f"{series!r}, which is not a series in "
                                        f"the manifest")
                    elif declared[series] != group:
                        problems.append(f"index.html: GROUPS[{group!r}] lists "
                                        f"{series!r}, but the manifest puts it "
                                        f"in {declared[series]!r}")
            labels = re.search(r'var LABELS = (\{.*?\});', index, re.S)
            if labels:
                try:
                    lab = json.loads(labels.group(1))
                except ValueError:
                    lab = None
                if lab is not None:
                    for group in sorted(groups):
                        if group not in lab:
                            problems.append(f"index.html: group {group!r} has no "
                                            f"entry in LABELS, so its chip will "
                                            f"not re-label after a reset")

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
