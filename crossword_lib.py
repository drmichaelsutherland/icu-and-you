#!/usr/bin/env python3
"""
ICU AND YOU — superpuzzle grid builder.

Places a word list into an interlocking crossword by best-fit search, then
emits the geometry the fillable and printable pages both need:

    GEOM = [{"n": clue number, "d": "A"|"D", "c": [[x, y], ...]}, ...]

Coordinates are zero-based, x across and y down. Numbering follows crossword
convention: scan row by row, and any cell that begins an across or a down
entry takes the next number.
"""

import random


class Grid:
    def __init__(self, size=30):
        self.size = size
        self.cells = {}                 # (x, y) -> letter
        self.placed = []                # (word, x, y, dir)

    def fits(self, word, x, y, d):
        dx, dy = (1, 0) if d == "A" else (0, 1)
        crossings = 0
        for i, ch in enumerate(word):
            cx, cy = x + i * dx, y + i * dy
            if not (0 <= cx < self.size and 0 <= cy < self.size):
                return None
            here = self.cells.get((cx, cy))
            if here:
                if here != ch:
                    return None
                crossings += 1
            else:
                # a new cell must not brush a parallel word
                if d == "A":
                    if self.cells.get((cx, cy - 1)) or self.cells.get((cx, cy + 1)):
                        return None
                else:
                    if self.cells.get((cx - 1, cy)) or self.cells.get((cx + 1, cy)):
                        return None
        # the ends must be clear, or words run together
        bx, by = x - dx, y - dy
        ax, ay = x + len(word) * dx, y + len(word) * dy
        if self.cells.get((bx, by)) or self.cells.get((ax, ay)):
            return None
        return crossings

    def place(self, word, x, y, d):
        dx, dy = (1, 0) if d == "A" else (0, 1)
        for i, ch in enumerate(word):
            self.cells[(x + i * dx, y + i * dy)] = ch
        self.placed.append((word, x, y, d))

    def candidates(self, word):
        out = []
        for (cx, cy), ch in list(self.cells.items()):
            for i, wch in enumerate(word):
                if wch != ch:
                    continue
                for d in ("A", "D"):
                    x = cx - i if d == "A" else cx
                    y = cy if d == "A" else cy - i
                    n = self.fits(word, x, y, d)
                    if n:
                        out.append((n, x, y, d))
        return out

    def extent(self):
        xs = [x for x, _ in self.cells]
        ys = [y for _, y in self.cells]
        return min(xs), min(ys), max(xs), max(ys)

    def normalise(self):
        x0, y0, _, _ = self.extent()
        self.cells = {(x - x0, y - y0): c for (x, y), c in self.cells.items()}
        self.placed = [(w, x - x0, y - y0, d) for w, x, y, d in self.placed]


def build(words, seed=0, tries=400):
    """Try many orderings; keep the tightest fully-connected grid."""
    best = None
    for t in range(tries):
        rnd = random.Random(seed + t)
        order = sorted(words, key=len, reverse=True)
        # keep the longest first, shuffle the tail for variety
        head, tail = order[:2], order[2:]
        rnd.shuffle(tail)
        g = Grid()
        g.place(head[0], 15, 15, "A")
        ok = True
        for w in head[1:] + tail:
            cands = g.candidates(w)
            if not cands:
                ok = False
                break
            # prefer more crossings, then a compact grid
            def score(c):
                n, x, y, d = c
                x0, y0, x1, y1 = g.extent()
                nx0, ny0 = min(x0, x), min(y0, y)
                nx1 = max(x1, x + (len(w) - 1 if d == "A" else 0))
                ny1 = max(y1, y + (len(w) - 1 if d == "D" else 0))
                area = (nx1 - nx0 + 1) * (ny1 - ny0 + 1)
                return (-n, area)
            cands.sort(key=score)
            n, x, y, d = cands[0]
            g.place(w, x, y, d)
        if not ok:
            continue
        g.normalise()
        x0, y0, x1, y1 = g.extent()
        w_, h_ = x1 + 1, y1 + 1
        # The series prints landscape (superpuzzle 47 is 45 x 22), so aspect
        # matters more than raw area: aim for roughly twice as wide as tall.
        aspect_miss = abs(w_ / max(h_, 1) - 2.2)
        key = (round(aspect_miss, 2), w_ * h_, -len(g.cells))
        if best is None or key < best[0]:
            best = (key, g, w_, h_)
    return best


def number(g):
    """Assign crossword numbers and return GEOM plus a number lookup."""
    starts = {}
    for w, x, y, d in g.placed:
        starts.setdefault((x, y), []).append((w, d))
    ordered = sorted(starts, key=lambda p: (p[1], p[0]))
    num = {p: i + 1 for i, p in enumerate(ordered)}

    geom, index = [], []
    for w, x, y, d in g.placed:
        dx, dy = (1, 0) if d == "A" else (0, 1)
        cells = [[x + i * dx, y + i * dy] for i in range(len(w))]
        geom.append({"n": num[(x, y)], "d": d, "c": cells})
        index.append((num[(x, y)], d, w, x, y))
    geom.sort(key=lambda e: (e["n"], e["d"]))
    index.sort()
    return geom, index
