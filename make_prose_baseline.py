#!/usr/bin/env python3
"""Regenerate prose_baseline.json — the list of shared wording audit.py accepts.

audit.py flags prose appearing on two to five pages, because that is what a
page built from another page and not rewritten looks like. Some sharing is
deliberate: a series explainer, a standing invitation, the Top Ten preamble.
Those live here, keyed by a hash of the text itself rather than by which pages
carry it, so adding a new piece to a series does not re-trigger its explainer.

Run this only when you have READ the flagged wording and decided it is meant
to be shared. Re-running it blindly after a real mistake would bless the
mistake, which is the one way this check can be defeated.

Usage:  python3 make_prose_baseline.py
"""
import hashlib, json, re
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
SITEWIDE = {"index.html", "about.html", "corrections.html", "glossary.html",
            "you-asked.html"}
MIN_WORDS, FURNITURE_AT = 14, 6

m = json.loads((HERE / "page_topic.json").read_text(encoding="utf-8"))
series_of = {p["file"]: p["series"] for p in m["pages"]}
label = {k: v[0] for k, v in m["series"].items()}

content = sorted(p.name for p in HERE.glob("*.html") if p.name not in SITEWIDE)
stem = lambda f: re.sub(r"-(fillable|printable|checklist)\.html$", ".html", f)

seen = defaultdict(set)
for f in content:
    s = (HERE / f).read_text(encoding="utf-8")
    s = re.sub(r"<style>.*?</style>|<script.*?</script>|<svg.*?</svg>|<!--.*?-->",
               "", s, flags=re.S)
    for c in re.findall(r"<p\b[^>]*>(.*?)</p>|<li\b[^>]*>(.*?)</li>", s, re.S):
        t = re.sub(r"<[^>]+>", " ", c[0] or c[1])
        t = re.sub(r"&[a-z]+;|&#\d+;", " ", t)
        t = re.sub(r"\s+", " ", t).strip()
        if len(t.split()) >= MIN_WORDS:
            seen[t].add(f)

out = {}
for t, ps in sorted(seen.items(), key=lambda kv: -len(kv[1])):
    if not (2 <= len(ps) < FURNITURE_AT):
        continue
    if len({stem(p) for p in ps}) == 1:
        continue
    sers = sorted({series_of[p] for p in ps if p in series_of})
    where = label[sers[0]] if len(sers) == 1 else "shared across series"
    out[hashlib.sha1(t.encode()).hexdigest()[:16]] = {
        "note": f"{where} — standing wording",
        "opening": " ".join(t.split()[:12]) + "…",
    }

(HERE / "prose_baseline.json").write_text(
    json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"prose_baseline.json — {len(out)} accepted shared blocks")
