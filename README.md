# ICU AND YOU

A comprehensive intensive care education programme, a topic at a time.
Written at Coffs Harbour Health Campus and published with GitHub Pages at
[icuandyou.com](https://icuandyou.com).

Free to read, no advertising, no login. Released under Creative Commons
BY-NC-SA.

## How the site works

**A topic sits for a fortnight.** Each block takes one subject and comes at it
from several directions, on the theory that people remember a thing they have
argued with, drawn and solved rather better than a thing they have been told.

**A base group appears with every topic.** The mind map, an aphorism worth
arguing with, a mnemonic, a crossword superpuzzle and a superquiz. These are
the spine of a block and they turn up every time.

**Everything else appears when it fits.** Pieces written for particular
audiences — medical students, nurses, GPs, emergency, anaesthetics — cultural
columns, a drug profile, a podcast or journal summary, a film, a book, a piece
for the general public. Some blocks carry several; some carry none. They are
chosen because the topic suits them, not to fill a slot.

**Some pieces belong to no topic at all.** Procedures, exam material, book
reviews and the monthly Top Ten are marked `"standing": true` in the manifest.
They drop out of the fortnight and collect in their own group on the landing
page.

**Subscribers get two emails a week** — the Friday newsletter for everyone, and
a Tuesday one for clinical subscribers carrying the new mind map and puzzles
before they appear here.

**And it keeps changing.** Series get added, renamed and retired; the structure
below describes how it works today rather than how it will always work.

## Structure

Flat. Every page sits in the repository root, named
`series-number-topic.html`, lowercase with hyphens:

```
mind-map-34-school-age.html
aphorism-38-little-adults.html
superpuzzle-50-toddler-preschool-fillable.html
superpuzzle-50-toddler-preschool.html          printable companion
procedures-03-urinary-catheterisation.html
```

Keeping the number in the filename keeps the listing in order.

Site-wide pages: `index.html`, `about.html`, `glossary.html`,
`corrections.html`, `you-asked.html`.

## The landing page is generated

**Do not hand-edit `index.html` between the build markers.** Regions marked
`<!-- BUILD:NAME -->` are written by `build-index.py` from `page_topic.json`.
Anything typed inside them is overwritten on the next build.

```
page_topic.json        the manifest: every page, its series, colour, topic,
                       blurb, and whether it is in the current fortnight
build-index.py         rebuilds the generated regions of index.html
audit.py               checks the whole site before publishing
```

Typical cycle:

1. Write the page.
2. Add an entry to `page_topic.json`. Set `"week": true` for pieces in the
   current fortnight, or `"standing": true` for those that belong to no topic.
3. `python3 build-index.py`
4. `python3 audit.py` — fix anything it reports.
5. Commit.

When a block ends, set the old pieces' `"week"` to `false`, add the new topic
to the top of `topic_order`, and update `teaser` in the manifest.

## Generators

```
mindmap_lib.py         renders a mind map from a content spec
mindmap_NN_spec.py     the content of one mind map; layout lives in the library
crossword_lib.py       builds and validates a superpuzzle grid
make_printable.py      generates the printable companion from a fillable puzzle
glossary.js            the definition cards behind dotted-underlined terms
```

## audit.py

Run it before every commit. It checks for orphan pages, dead links, missing
meta descriptions, missing disclaimers and subscribe lines, glossary links with
no entry, series links that resolve to no filter, mind map text that will
overflow its card, and puzzle grids whose dimensions do not match their cells.

Most of those checks exist because something went wrong once.

## Before you publish

**The repository is public**, and so is anything in it. Never commit an answer
key, and never commit anything with a patient detail in it. Marker's copies
stay on the local machine.

**Every page carries the standing statements** — that the material is
educational and not a clinical protocol, that local policy and current guidance
take precedence, that doses must be verified, that no identifiable patient is
described, and that the views are the author's own. New pages need them too;
`audit.py` checks.

## Contact

Corrections and replies to `icuandyou@icloud.com`. Anything that could affect
care is fixed the same day, or the page comes down until it can be. Whoever
found it is credited by name unless they would rather not be.
