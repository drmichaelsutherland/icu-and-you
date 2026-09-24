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
Run  python3 build-index-2.py --insert-markers  once to add them.

Usage:
    python3 build-index-2.py                 rewrite index.html in place
    python3 build-index-2.py --check         report what would change, write nothing
    python3 build-index-2.py --insert-markers
"""

import collections
import json
import re
import sys
from html import escape
from html.parser import HTMLParser
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
# search terms
# --------------------------------------------------------------------------
#
# The landing-page search only ever saw what was printed in the row: series,
# number and title, plus the topic heading above it. So a reader looking for
# dengue, or for Peter Pan, got nothing, because neither word appears in the
# row that leads to the piece. Proper full-text search is a separate job; this
# is the cheap eighty per cent. Each row carries a hidden bag of the words that
# distinguish its page, harvested from the page itself at build time, so a new
# piece becomes searchable the moment it is added with no manifest work at all.
#
# "Distinguish" is the whole trick. A word that turns up on a dozen pages —
# child, clinical, published — tells a searcher nothing, so it is dropped. What
# survives is what is peculiar to this page: its proper nouns, its headings,
# the terms it returns to. An absolute cutoff rather than a proportion of the
# corpus keeps the output steady: a word crosses the line once, on the build
# after it becomes common, instead of every page's list reshuffling each time
# the site grows.

WORD = r"[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ'’-]{2,}"
COMMON_AT = 12   # a word on this many pages or more has stopped distinguishing
TERMS_PER_PAGE = 30
COMMON_KEPT_AT = 4    # ...unless the page returns to it this often, or heads a section with it
COMMON_PER_PAGE = 8


class _Prose(HTMLParser):
    """Visible text, with the headings kept separately so they can be weighted."""

    def __init__(self):
        super().__init__()
        self.skip = 0
        self.body = []
        self.heads = []
        self._h = None

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1
        elif tag in ("h1", "h2", "h3"):
            self._h = []

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self.skip:
            self.skip -= 1
        elif tag in ("h1", "h2", "h3") and self._h is not None:
            self.heads.append(" ".join(self._h))
            self._h = None

    def handle_data(self, data):
        if self.skip:
            return
        self.body.append(data)
        if self._h is not None:
            self._h.append(data)


def _read_prose(m):
    """{file: (body, headings)} for every page the manifest lists that exists."""
    out = {}
    for pg in m["pages"]:
        path = HERE / pg["file"]
        if not path.exists():
            continue
        p = _Prose()
        p.feed(path.read_text(encoding="utf-8"))
        out[pg["file"]] = (" ".join(p.body), " ".join(p.heads))
    return out


def terms_attr(m, page):
    """The data-k attribute for one page's row or card, empty if unharvested."""
    t = m.get("_terms", {}).get(page["file"], "")
    return f' data-k="{e(t)}"' if t else ""


def build_terms(m):
    """{file: "word word word"} — the search bag for each page."""
    prose = _read_prose(m)
    pages = collections.Counter()
    for body, _ in prose.values():
        for w in set(re.findall(WORD, body)):
            pages[w.lower()] += 1

    blurbs = {pg["file"]: pg.get("blurb", "") for pg in m["pages"]}
    extra = {pg["file"]: pg.get("keywords", "") for pg in m["pages"]}

    terms = {}
    for f, (body, heads) in prose.items():
        freq = collections.Counter(w.lower() for w in re.findall(WORD, body))
        in_head = {w.lower() for w in re.findall(WORD, heads)}
        # A capitalised word mid-sentence is a name, a place or a trade name,
        # which is exactly what a reader is most likely to search for.
        proper = {w.lower() for w in
                  re.findall(r"(?<!^)(?<![.!?][ \n])\b[A-ZÀ-Þ][a-zà-ÿ]{2,}", body)}
        scored, carried = {}, {}
        for w, n in freq.items():
            if pages[w] >= COMMON_AT:
                # Common across the site, but a word can be common here and
                # still be what this page is about — sepsis runs through a
                # dozen pieces and is the subject of two. Keep it where the
                # page carries it in a heading or keeps returning to it, in a
                # bucket of its own so that it cannot crowd out a name or a
                # term that occurs once and belongs to this page alone.
                if w in in_head or n >= COMMON_KEPT_AT:
                    carried[w] = n
            elif n >= 2 or w in in_head or w in proper:
                scored[w] = n + (6 if w in in_head else 0) + (3 if w in proper else 0)
        keep = sorted(scored, key=lambda w: (-scored[w], w))[:TERMS_PER_PAGE]
        keep += sorted(carried, key=lambda w: (-carried[w], w))[:COMMON_PER_PAGE]
        # The blurb is already written for the reader and the keywords field is
        # there for hand-correcting a miss; both go in whole, over the cap.
        keep += re.findall(WORD, blurbs.get(f, "").lower())
        keep += re.findall(WORD, extra.get(f, "").lower())
        # Alphabetical, so a rebuild that changes nothing produces no diff.
        terms[f] = " ".join(sorted(set(keep)))
    return terms


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
            f'        <li class="item {p["colour"]}" data-series="{series_attr}"'
            f'{terms_attr(m, p)}>',
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
    # Most recent topic first. Pages carry no dates and manifest position is not
    # a reliable proxy — the early blocks were not entered in the order they ran
    # — so the sequence is declared explicitly in "topic_order", newest first.
    # Any slug not listed there falls to the end, in manifest order.
    declared = m.get("topic_order", [])
    rank = {slug: i for i, slug in enumerate(declared)}
    seen, topics = [], {}
    for p in m["pages"]:
        if p.get("standing") or p.get("week"):
            continue
        if p["slug"] not in topics:
            topics[p["slug"]] = p["topic"]
            seen.append(p["slug"])
    order = [(slug, topics[slug])
             for slug in sorted(seen, key=lambda k: (rank.get(k, len(declared)),
                                                     seen.index(k)))]

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
                f'            <li class="row {p["colour"]}" data-series="{series_attr}"'
                f'{terms_attr(m, p)}>'
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
            '          <span class="tname">Any time. Not tied to a particular topic grouping</span>',
            f'          <span class="tdots">{dots}</span>',
            f'          <span class="tcount">{n} piece{"s" if n != 1 else ""}</span>',
            '        </summary>',
            '        <ul class="rows">',
        ]
        for p in standing:
            label = m["series"][p["series"]][0]
            series_attr = " ".join([p["series"]] + p.get("guests", []))
            out.append(
                f'            <li class="row {p["colour"]}" data-series="{series_attr}"'
                f'{terms_attr(m, p)}>'
                f'<span class="rs">{e(label)}</span>'
                f'<span class="rn">{e(p.get("number") or "")}</span>'
                f'<a class="rt" href="{p["file"]}">{e(p["title"])}</a></li>')
        out += ['        </ul>', '      </details>']
    return "\n".join(out)


def build_latest(m):
    out = ['        <div class="menu">']
    items = m["latest"]
    # an entry pointing at a section that is switched off would be a dead
    # anchor, so drop it with the section
    if not m.get("donation_promo", True):
        items = [x for x in items if x["file"] != "#donate"]
    for x in items:
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


def build_donate_line(m):
    """The one-line mention beside "New here?" on the strip. Controlled by
    "donation_promo" in the manifest so it can be switched off wholesale."""
    if not m.get("donation_promo", True):
        return ""
    return ('          <p class="donateline">This site supports organ donation '
            'registration &mdash; <a href="#donate">register your decision</a>.</p>')


def build_donate(m):
    """The organ donor register section at the foot of the landing page.
    Same switch. The QR is inline SVG and lives in the manifest so the
    landing page and the six donation pages cannot drift apart."""
    if not m.get("donation_promo", True):
        return ""
    d = m.get("donation", {})
    lis = "\n".join(f'        <li>{e(x)}</li>' for x in d.get("points", []))
    return f'''  <section class="sub" id="donate">
    <h2>{e(d.get("heading", "Organ and tissue donation"))}</h2>
    <p>Scan the code, or go to
      <a href="{d.get("url", "")}">donatelife.gov.au</a>.</p>
    <div class="odr">
      <div class="qr">{d.get("qr", "")}</div>
      <ul>
{lis}
      </ul>
    </div>
  </section>'''


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


def build_topics(m):
    """The topic index in the control bar. Topics accumulate as the programme
    works along the lifespan, and the only other way to reach one is to scroll
    past everything above it. Order follows topic_order; the standing archive
    goes last because it is not a topic. Counts come from the manifest so the
    list cannot drift from what is actually on the page."""
    counts, labels, seen = {}, {}, []
    for pg in m["pages"]:
        if pg.get("standing"):
            counts["standing"] = counts.get("standing", 0) + 1
            labels["standing"] = "Any time"
            continue
        slug = pg["slug"]
        if slug not in counts:
            seen.append(slug)
            labels[slug] = pg["topic"]
        counts[slug] = counts.get(slug, 0) + 1
    declared = m.get("topic_order", [])
    rank = {slug: i for i, slug in enumerate(declared)}
    order = sorted(seen, key=lambda k: (rank.get(k, len(declared)), seen.index(k)))
    if "standing" in counts:
        order.append("standing")
    out = ['        <div class="menu">']
    for slug in order:
        out.append(
            f'          <button class="mi" data-t="{e(slug)}">'
            f'<i class="md topic"></i>{e(labels[slug])}'
            f'<span class="tcount">{counts[slug]}</span></button>')
    out.append('        </div>')
    return "\n".join(out)


REGIONS = {
    "TEASER": build_teaser,
    "DONATE-LINE": build_donate_line,
    "DONATE": build_donate,
    "PROCEDURES": build_procedures,
    "THIS-WEEK": build_this_week,
    "PREVIOUS-WEEKS": build_previous,
    "LATEST": build_latest,
    "TOPTEN": build_topten,
    "TOPICS": build_topics,
}


# --------------------------------------------------------------------------
# marker insertion (one-off)
# --------------------------------------------------------------------------

def insert_markers(src):
    """Wrap the four existing regions in marker comments. Idempotent."""
    def wrap(src, name, pattern):
        # match the whole marker, not a prefix: BUILD:DONATE must not be
        # satisfied by BUILD:DONATE-LINE
        if f"<!-- BUILD:{name} -->" in src:
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
    src = wrap(src, "DONATE-LINE", r'          <p class="donateline">.*?</p>')
    src = wrap(src, "DONATE", r'  <section class="sub" id="donate">.*?</section>')
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
        print("Done. Commit this, then build-index-2.py can run normally.")
        return

    m = load()
    # Harvested once and shared by the builders that emit rows and cards.
    m["_terms"] = build_terms(m)
    missing = [n for n in REGIONS if f"<!-- BUILD:{n} -->" not in src]
    if missing:
        sys.exit(f"index.html has no markers for: {', '.join(missing)}\n"
                 f"Run:  python3 build-index-2.py --insert-markers")

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
