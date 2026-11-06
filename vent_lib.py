#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Original ventilator waveform figures for Your Presentations No. 3.

The source deck carried these as screenshots of published figures, so they are
rebuilt here from the underlying physiology. Nothing is traced. Each waveform is
computed from a model of the breath and then drawn, which is why the pressure
trace in volume control slopes and the one in pressure control does not: it
falls out of the arithmetic rather than being copied.

Conventions, so every figure on the page reads the same way:
    pressure  rust    flow  green    volume  blue
    time runs left to right, seconds, with the same scale in every panel
"""
import math

INK   = "#201B26"
MUTED = "#6B6473"
RULE  = "#CFC8D8"
GRID  = "#EFEBF4"
PRESS = "#A8442A"
FLOW  = "#3E7730"
VOL   = "#2F4A7C"
CALL  = "#473C56"
CALLBG= "#F1EEF6"

FONT = "'Helvetica Neue',Arial,sans-serif"


# ---------------------------------------------------------------- breath models
def pc_breath(t, ti, pset, peep, tau=0.42):
    """Pressure control. Square pressure; flow decelerates as alveolar pressure
    approaches the set pressure; volume fills exponentially."""
    if t < ti:
        p = peep + pset
        f = 62 * math.exp(-t / tau)
        v = 520 * (1 - math.exp(-t / tau))
    else:
        te = t - ti
        p = peep
        f = -58 * math.exp(-te / 0.45)
        v = 520 * math.exp(-te / 0.45) * (1 - math.exp(-ti / tau)) / (1 - math.exp(-ti / tau))
        v = 520 * (1 - math.exp(-ti / tau)) * math.exp(-te / 0.45)
    return p, f, v


def vc_breath(t, ti, flow, peep, raw=7.0, comp=45.0):
    """Volume control, constant inspiratory flow. Pressure = resistive step +
    a ramp that is the volume accumulating against compliance."""
    if t < ti:
        v = flow * 1000 / 60 * t                     # L/min -> mL/s
        p = peep + (flow / 60) * raw + v / comp
        f = flow
    else:
        te = t - ti
        vt = flow * 1000 / 60 * ti
        v = vt * math.exp(-te / 0.45)
        p = peep
        f = -(flow * 1.05) * math.exp(-te / 0.45)
    return p, f, v


def sample(fn, t0, dur, n=240, **kw):
    out = []
    for i in range(n + 1):
        t = dur * i / n
        out.append((t0 + t,) + fn(t, **kw))
    return out


# ---------------------------------------------------------------- drawing frame
class Fig:
    RPAD = 26

    def __init__(self, title, tmax=8.0, width=680, panels=None, pad_left=62, top=24):
        self.title = title
        self.tmax = tmax
        self.W = width
        self.pad = pad_left
        self.top = top
        self.panels = panels or []
        self.parts = []
        self.H = top

    def add_panel(self, key, label, lo, hi, h=92, gap=16):
        y0 = self.H
        self.panels.append(dict(key=key, label=label, lo=lo, hi=hi, y0=y0, h=h))
        self.H = y0 + h + gap
        return self.panels[-1]

    def P(self, key):
        for p in self.panels:
            if p["key"] == key:
                return p
        raise KeyError(key)

    def x(self, t):
        return self.pad + (self.W - self.pad - self.RPAD) * (t / self.tmax)

    def y(self, key, v):
        p = self.P(key)
        frac = (v - p["lo"]) / (p["hi"] - p["lo"])
        return p["y0"] + p["h"] - frac * p["h"]

    # ---- primitives
    def path(self, key, pts, colour, w=2.4, dash=None, idx=1):
        d = []
        for i, (t, v) in enumerate(pts):
            d.append(("M" if i == 0 else "L") + "%.1f %.1f" % (self.x(t), self.y(key, v)))
        self.parts.append('<path d="%s" fill="none" stroke="%s" stroke-width="%s"%s '
                          'stroke-linejoin="round" stroke-linecap="round"/>'
                          % (" ".join(d), colour, w,
                             ' stroke-dasharray="%s"' % dash if dash else ""))

    def hline(self, key, v, colour=RULE, dash="4 4", w=1):
        self.parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                          'stroke-width="%s"%s/>'
                          % (self.pad, self.y(key, v), self.W - self.RPAD, self.y(key, v),
                             colour, w, ' stroke-dasharray="%s"' % dash if dash else ""))

    def vline(self, key, t, colour=RULE, dash="3 4", lo=None, hi=None):
        p = self.P(key)
        y1 = self.y(key, hi) if hi is not None else p["y0"]
        y2 = self.y(key, lo) if lo is not None else p["y0"] + p["h"]
        self.parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                          'stroke-width="1" stroke-dasharray="%s"/>'
                          % (self.x(t), y1, self.x(t), y2, colour, dash))

    def label(self, x, y, text, size=12.5, colour=MUTED, anchor="start", weight=400, style=""):
        self.parts.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="%s" '
                          'font-weight="%s" fill="%s" text-anchor="%s"%s>%s</text>'
                          % (x, y, FONT, size, weight, colour, anchor,
                             ' font-style="italic"' if style == "i" else "", text))

    def callout(self, x, y, text, to=None, colour=CALL, anchor="start", size=12):
        """A small annotation with an optional leader line to a point."""
        if to:
            self.parts.append('<path d="M%.1f %.1f L%.1f %.1f" fill="none" stroke="%s" '
                              'stroke-width="1" stroke-dasharray="2 3"/>'
                              % (x, y + 4, to[0], to[1], RULE))
            self.parts.append('<circle cx="%.1f" cy="%.1f" r="2.4" fill="%s"/>' % (to[0], to[1], colour))
        self.label(x, y, text, size=size, colour=colour, anchor=anchor, weight=600)

    def brace(self, key, t, v1, v2, text, side="right", dx=10):
        """A vertical measure between two values at time t."""
        x = self.x(t) + dx
        y1, y2 = self.y(key, v1), self.y(key, v2)
        self.parts.append('<path d="M%.1f %.1f L%.1f %.1f M%.1f %.1f L%.1f %.1f '
                          'M%.1f %.1f L%.1f %.1f" fill="none" stroke="%s" stroke-width="1"/>'
                          % (x - 4, y1, x + 4, y1, x - 4, y2, x + 4, y2, x, y1, x, y2, CALL))
        self.label(x + 7, (y1 + y2) / 2 + 4, text, size=11.5, colour=CALL, weight=600)

    def axes(self, time_axis=True):
        for p in self.panels:
            base = p["y0"] + p["h"] if p["lo"] >= 0 else self.y(p["key"], 0)
            self.parts.insert(0, '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" '
                                 'stroke="%s" stroke-width="1.4"/>'
                              % (self.pad, base, self.W - self.RPAD, base, "#9D93AE"))
            self.parts.insert(0, '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" '
                                 'fill="%s" rx="3"/>'
                              % (self.pad, p["y0"], self.W - self.RPAD - self.pad, p["h"], GRID))
            self.label(self.pad - 9, p["y0"] + p["h"] / 2 + 4, p["label"],
                       size=11.5, colour=MUTED, anchor="end", weight=600)
        if time_axis:
            yb = self.H - 2
            for s in range(0, int(self.tmax) + 1, 1):
                self.parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" '
                                  'stroke="%s" stroke-width="1"/>'
                                  % (self.x(s), yb - 4, self.x(s), yb, RULE))
                if s % 2 == 0:
                    self.label(self.x(s), yb + 13, str(s), size=11, colour=MUTED, anchor="middle")
            self.H += 20

    def legend(self, items):
        """Coloured keys along the top band: (colour, text), left to right."""
        x = self.pad
        for colour, text in items:
            self.parts.append('<rect x="%.1f" y="%.1f" width="15" height="3.5" rx="1.7" '
                              'fill="%s"/>' % (x, self.top - 15, colour))
            self.label(x + 21, self.top - 11, text, size=11.5, colour=MUTED, weight=600)
            x += 26 + 7.1 * len(text)

    def svg(self):
        self.H += 6
        return ('<svg viewBox="0 0 %d %d" width="100%%" '
                'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="%s">\n'
                '<title>%s</title>\n%s\n</svg>'
                % (self.W, self.H, self.title, self.title, "\n".join(self.parts)))
