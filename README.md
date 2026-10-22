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
prose_baseline.json    wording that is SHARED BETWEEN PAGES on purpose
make_prose_baseline.py regenerates that file — only after reading what changed
```

Typical cycle:

1. Write the page.
2. Add an entry to `page_topic.json`. Set `"week": true` for pieces in the
   current fortnight, or `"standing": true` for those that belong to no topic.
3. `python3 build-index.py`
4. `python3 audit.py` — fix anything it reports.
5. **Read the new page through, start to finish**, as a reader would. The
   audit cannot tell you that a sentence is about the wrong age group, that
   an argument does not land, or that the challenge is the wrong question.
6. Commit.

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
overflow its card, puzzle grids whose dimensions do not match their cells,
classes used in the markup that nothing styles, scaffolding left in a finished
page, and prose carried over from the page a new page was built from.

Most of those checks exist because something went wrong once.

### Inherited prose

Every page here is built from an earlier one, which is how the house style
stays consistent — and it means an unrewritten paragraph is invisible. Mind
Map 36 published with Mind Map 35's entire opening, three paragraphs about
adolescents, and every other check passed: the page was valid, linked
correctly, rendered correctly, and was about the wrong patient.

So `audit.py` flags prose appearing on two to five pages. Wording on more
pages than that is furniture; a paragraph on two or three was copied and
forgotten. Companion pages of the same piece — a printable and its fillable,
a checklist and its long version — are exempt, because there the copying is
the point.

Deliberate sharing lives in `prose_baseline.json`, keyed by a hash of the
text rather than by which pages carry it, so adding a new piece to a series
does not re-trigger its explainer. When the audit flags something, **read it**
and then either fix the page or paste the printed line into the baseline.
Running `make_prose_baseline.py` to clear a report without reading it would
bless the mistake, which is the only way this check can be defeated.

The footer counts. The first version of this check read only `<p>` and `<li>`,
so it could not see the footer — and Mind Map 36 went up a second time with an
inherited line, this time the source credit, naming the ANZPIC registry, the
Immunisation Handbook and Australian anaphylaxis series on a page about
eighteen to thirty year olds. Widening it to footer text found two more at
once: Podcast 58 was crediting Podcast 57's episode, host and date, and
Literary Edge 2 said it quoted the King James Version and deferred to Red Nose
on safe sleeping, on a page about *Peter Pan*. Misattributing somebody else's
podcast is the worst of those three, and nothing but this check was ever going
to find it.

### Scaffolding

A one-line check for `PLACEHOLDER`, `TODO`, `FIXME`, `TBC`, `lorem ipsum` and
the like. Pages here get built in stages — prose first, a source line or a
figure filled in once it has been verified — and a placeholder is by
definition something that looked fine at the moment it was typed. Matched
case-sensitively on purpose: the India Room page says its own name "is a
placeholder", and every quiz has an input with `placeholder="Type your name"`.

## Before you publish

**The repository is public**, and so is anything in it. Never commit an answer
key, and never commit anything with a patient detail in it. Marker's copies
stay on the local machine.

**Every page carries the standing statements** — that the material is
educational and not a clinical protocol, that local policy and current guidance
take precedence, that doses must be verified, that no identifiable patient is
described, and that the views are the author's own. New pages need them too;
`audit.py` checks.

**Material submitted by other people needs an image-provenance check before
anything goes up.** Teaching slides are almost always built from screenshots of
guidelines, textbooks and journals. That is ordinary fair dealing in a tutorial
room and straightforward infringement on a public website, and it is this site
that would be publishing it. Unpack the file, look at every embedded image, and
assume a figure is third-party until shown otherwise — one of the first deck's
images still carried the publisher's copyright line inside the artwork.

The remedy is not to crop the notice off. Facts are not copyright, only the
particular expression of them, so a borrowed table gets rebuilt from the
underlying clinical facts as the site's own markup, and the source is credited
in the footer. `audit.py` cannot see any of this; it is a human step.

## Contact

Corrections and replies to `icuandyou@icloud.com`. Anything that could affect
care is fixed the same day, or the page comes down until it can be. Whoever
found it is credited by name unless they would rather not be.
