#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The twelve figures for Your Presentations No. 3, built on vent_lib.

Run:  python3 vent_figures.py <output-directory>
Each figure is computed from a model of the breath rather than traced from
anything, which is the point: the source deck carried its figures as
screenshots of published material and none of them could be republished."""
import math, sys
sys.path.insert(0, __import__("os").path.dirname(__file__) or ".")
from vent_lib import (Fig, pc_breath, vc_breath, sample,
                      PRESS, FLOW, VOL, MUTED, CALL, RULE, INK)

PEEP, TI, TCYC = 5, 1.0, 2.0


def _three(title, tmax=8.0, w=680):
    f = Fig(title, tmax=tmax, width=w)
    f.add_panel("p", "Pressure", -2, 34)
    f.add_panel("f", "Flow", -70, 70)
    f.add_panel("v", "Volume", 0, 620)
    return f


def _run(f, model, n_breaths=4, tcyc=TCYC, **kw):
    """Lay consecutive identical breaths end to end and draw the three traces."""
    P, F, V = [], [], []
    for b in range(n_breaths):
        t0 = b * tcyc
        for t, p, fl, v in sample(model, t0, tcyc, n=160, **kw):
            if t > f.tmax:
                break
            P.append((t, p)); F.append((t, fl)); V.append((t, v))
    f.path("p", P, PRESS); f.path("f", F, FLOW); f.path("v", V, VOL)
    return P, F, V


# ------------------------------------------------------------------ 1. PC vs VC
def pressure_control():
    f = _three("Pressure control: square pressure waveform, decelerating flow, variable tidal volume")
    _run(f, pc_breath, ti=TI, pset=15, peep=PEEP)
    f.hline("p", PEEP + 15, RULE)
    f.axes()
    f.legend([(PRESS, "Pressure"), (FLOW, "Flow"), (VOL, "Volume")])
    f.label(f.W - f.RPAD, f.y("p", 22) - 7, "set pressure", size=11.5, colour=PRESS,
            anchor="end", weight=600)
    f.callout(f.x(1.15), f.y("f", 50), "decelerating", anchor="start", size=11.5)
    f.callout(f.x(1.15), f.y("v", 430), "volume varies", anchor="start", size=11.5)
    return f.svg()


def volume_control():
    f = _three("Volume control: constant inspiratory flow, sloping pressure, guaranteed tidal volume")
    _run(f, vc_breath, ti=TI, flow=30, peep=PEEP)
    f.axes()
    f.legend([(PRESS, "Pressure"), (FLOW, "Flow"), (VOL, "Volume")])
    f.callout(f.x(1.15), f.y("p", 28), "pressure rises", anchor="start", size=11.5)
    f.callout(f.x(1.15), f.y("f", 50), "flow is square", anchor="start", size=11.5)
    f.callout(f.x(1.15), f.y("v", 430), "volume is set", anchor="start", size=11.5)
    return f.svg()


# ------------------------------------------------------- 2. the pressure anatomy
def pressure_anatomy():
    """Peak, plateau, PEEP, and what the two gaps mean. Volume control with an
    inspiratory hold, which is the only way the plateau is visible."""
    f = Fig("The pressure waveform: peak, plateau and PEEP, with an inspiratory hold",
            tmax=5.0, width=680)
    f.add_panel("p", "Pressure", -2, 40, h=150)
    PK, PLAT = 32, 22
    pts = [(0, PEEP), (0.08, PEEP + 5)]
    for i in range(1, 41):
        t = 0.08 + 0.92 * i / 40
        pts.append((t, PEEP + 5 + (PK - PEEP - 5) * (i / 40)))
    pts += [(1.0, PK), (1.02, PLAT + 1.5), (1.05, PLAT), (2.0, PLAT),
            (2.05, PEEP), (5.0, PEEP)]
    f.path("p", pts, PRESS, w=2.6)
    for v, lab in ((PK, "Peak"), (PLAT, "Plateau"), (PEEP, "PEEP")):
        f.hline("p", v, RULE)
    f.axes(time_axis=False)
    f.label(f.W - f.RPAD, f.y("p", PK) - 7, "peak", size=12, colour=PRESS, anchor="end", weight=600)
    f.label(f.W - f.RPAD, f.y("p", PLAT) - 7, "plateau", size=12, colour=PRESS, anchor="end", weight=600)
    f.label(f.W - f.RPAD, f.y("p", PEEP) - 7, "PEEP", size=12, colour=PRESS, anchor="end", weight=600)
    f.brace("p", 2.15, PK, PLAT, "resistance", dx=12)
    f.brace("p", 2.15, PLAT, PEEP, "compliance (driving pressure)", dx=12)
    return f.svg()


# ---------------------------------------------------------------- 3. resistance
def resistance():
    f = Fig("Raised airway resistance widens the gap between peak and plateau pressure",
            tmax=8.0, width=680)
    f.add_panel("p", "Pressure", -2, 44, h=132)

    def breath(t0, peak, plat):
        pts = [(t0, PEEP), (t0 + .06, PEEP + (peak - plat) * .75)]
        for i in range(1, 31):
            t = t0 + .06 + .94 * i / 30
            pts.append((t, PEEP + (peak - plat) * .75 + (plat - PEEP) * (i / 30) + (peak - plat) * .25 * (i / 30)))
        pts += [(t0 + 1.0, peak), (t0 + 1.03, plat), (t0 + 1.5, plat),
                (t0 + 1.56, PEEP), (t0 + 2.0, PEEP)]
        return pts

    for t0 in (0.4, 2.4):
        f.path("p", [q for q in breath(t0, 38, 22) if q[0] <= f.tmax], PRESS)
    for t0 in (4.6, 6.4):
        f.path("p", [q for q in breath(t0, 26, 22) if q[0] <= f.tmax], PRESS)
    f.hline("p", 22, RULE)
    f.axes()
    f.callout(f.x(0.4), f.y("p", 42), "High airway resistance", anchor="start")
    f.callout(f.x(4.6), f.y("p", 42), "Normal airway resistance", anchor="start")
    f.brace("p", 1.45, 38, 22, "wide", dx=8)
    f.brace("p", 5.45, 26, 22, "narrow", dx=8)
    return f.svg()


# ---------------------------------------------------------------- 4. compliance
def compliance():
    f = Fig("Falling compliance raises the plateau pressure, with the peak-to-plateau gap unchanged",
            tmax=8.0, width=680)
    f.add_panel("p", "Pressure", -2, 44, h=132)

    def breath(t0, peak, plat):
        pts = [(t0, PEEP), (t0 + .06, PEEP + (peak - plat) * .8)]
        for i in range(1, 31):
            t = t0 + .06 + .94 * i / 30
            pts.append((t, PEEP + (peak - plat) * .8 + (plat - PEEP) * (i / 30) + (peak - plat) * .2 * (i / 30)))
        pts += [(t0 + 1.0, peak), (t0 + 1.03, plat), (t0 + 1.5, plat),
                (t0 + 1.56, PEEP), (t0 + 2.0, PEEP)]
        return pts

    for t0 in (0.4, 2.4):
        f.path("p", [q for q in breath(t0, 36, 31) if q[0] <= f.tmax], PRESS)
    for t0 in (4.6, 6.4):
        f.path("p", [q for q in breath(t0, 21, 16) if q[0] <= f.tmax], PRESS)
    f.hline("p", 31, RULE); f.hline("p", 16, RULE); f.hline("p", 30, "#C3AFA8")
    f.axes()
    f.callout(f.x(0.4), f.y("p", 42), "Poor compliance", anchor="start")
    f.callout(f.x(4.6), f.y("p", 42), "Good compliance", anchor="start")
    f.label(f.W - f.RPAD, f.y("p", 30) - 5, "plateau 30", size=11, colour="#A3847B",
            anchor="end", weight=600)
    return f.svg()


# ------------------------------------------------------- 5. pressure support
def pressure_support():
    f = _three("Pressure support: the patient triggers, the ventilator supports, flow ends the breath")
    P, F, V = [], [], []
    for b in range(4):
        t0 = b * 2.0
        P += [(t0, PEEP), (t0 + .10, PEEP - 2.2), (t0 + .16, PEEP + 14), (t0 + .2, PEEP + 15)]
        F += [(t0, 0), (t0 + .10, -9), (t0 + .16, 58)]
        V += [(t0, 0), (t0 + .16, 10)]
        for i in range(1, 45):
            t = t0 + .2 + 0.75 * i / 45
            P.append((t, PEEP + 15))
            F.append((t, 58 * math.exp(-(t - t0 - .16) / 0.40)))
            V.append((t, 520 * (1 - math.exp(-(t - t0 - .16) / 0.40))))
        tc = t0 + 0.95
        P += [(tc, PEEP + 15), (tc + .04, PEEP)]
        F += [(tc, 58 * math.exp(-0.79 / 0.40)), (tc + .04, -54)]
        vt = 520 * (1 - math.exp(-0.79 / 0.40))
        V += [(tc, vt)]
        for i in range(1, 40):
            t = tc + .04 + 1.0 * i / 40
            if t > f.tmax: break
            P.append((t, PEEP)); F.append((t, -54 * math.exp(-(t - tc) / 0.42)))
            V.append((t, vt * math.exp(-(t - tc) / 0.42)))
    f.path("p", [q for q in P if q[0] <= f.tmax], PRESS)
    f.path("f", [q for q in F if q[0] <= f.tmax], FLOW)
    f.path("v", [q for q in V if q[0] <= f.tmax], VOL)
    f.hline("f", 58 * 0.25, "#9BB894")
    f.axes()
    f.legend([(PRESS, "Pressure"), (FLOW, "Flow"), (VOL, "Volume")])
    f.callout(f.x(2.45), f.y("p", 26), "the patient triggers it",
              to=(f.x(2.12), f.y("p", PEEP - 2.2)), anchor="start", size=11.5)
    f.label(f.x(0.12), f.y("f", -44), "cycles off at 25% of peak flow", size=11.5,
            colour="#4E7A44", weight=600)
    return f.svg()


# --------------------------------------------------------------------- 6. SIMV
def simv():
    f = _three("SIMV: a guaranteed mandatory breath in each window, with supported breaths between")
    P, F, V = [], [], []
    for b in range(4):
        t0 = b * 2.0
        mand = b % 2 == 0
        if mand:
            for t, p, fl, v in sample(vc_breath, t0, 2.0, n=120, ti=TI, flow=30, peep=PEEP):
                if t <= f.tmax:
                    P.append((t, p)); F.append((t, fl)); V.append((t, v))
        else:
            P += [(t0, PEEP), (t0 + .10, PEEP - 2.0), (t0 + .16, PEEP + 10)]
            F += [(t0, 0), (t0 + .10, -8), (t0 + .16, 44)]
            V += [(t0, 0)]
            for i in range(1, 40):
                t = t0 + .16 + 0.7 * i / 40
                P.append((t, PEEP + 10))
                F.append((t, 44 * math.exp(-(t - t0 - .16) / 0.38)))
                V.append((t, 360 * (1 - math.exp(-(t - t0 - .16) / 0.38))))
            tc = t0 + 0.86
            P += [(tc + .04, PEEP)]
            F += [(tc + .04, -40)]
            for i in range(1, 36):
                t = tc + .04 + 1.05 * i / 36
                if t > f.tmax: break
                P.append((t, PEEP)); F.append((t, -40 * math.exp(-(t - tc) / 0.40)))
                V.append((t, 350 * math.exp(-(t - tc) / 0.40)))
    f.path("p", [q for q in P if q[0] <= f.tmax], PRESS)
    f.path("f", [q for q in F if q[0] <= f.tmax], FLOW)
    f.path("v", [q for q in V if q[0] <= f.tmax], VOL)
    for t0 in (0, 4):
        f.parts.insert(0, '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#E4DEEE" '
                          'rx="3"/>' % (f.x(t0), f.P("p")["y0"], f.x(t0 + 1.2) - f.x(t0),
                                        f.P("v")["y0"] + f.P("v")["h"] - f.P("p")["y0"]))
    f.axes()
    f.legend([(PRESS, "Pressure"), (FLOW, "Flow"), (VOL, "Volume")])
    f.label(f.W - f.RPAD, f.top - 11, "shaded: the trigger window", size=11.5,
            colour=CALL, weight=600, anchor="end")
    f.callout(f.x(2.1), f.y("p", 27), "supported breath", anchor="start", size=11.5)
    return f.svg()


# ------------------------------------------------------- 7. dynamic hyperinflation
def gas_trapping():
    f = Fig("Gas trapping: expiratory flow has not returned to zero when the next breath begins",
            tmax=8.0, width=680)
    f.add_panel("f", "Flow", -70, 70, h=140)
    pts = []
    for b in range(5):
        t0 = b * 1.6
        pts += [(t0, -16 if b else 0), (t0 + .02, 58)]
        for i in range(1, 26):
            t = t0 + .02 + .62 * i / 25
            pts.append((t, 58))
        pts += [(t0 + .64, 58), (t0 + .66, -56)]
        for i in range(1, 40):
            t = t0 + .66 + .94 * i / 40
            if t > f.tmax: break
            pts.append((t, -56 * math.exp(-(t - t0 - .66) / 0.68)))
    f.path("f", [q for q in pts if q[0] <= f.tmax], FLOW)
    f.hline("f", 0, "#9D93AE", dash=None)
    f.axes()
    for t0 in (1.6, 3.2, 4.8, 6.4):
        f.parts.append('<circle cx="%.1f" cy="%.1f" r="3.4" fill="none" stroke="%s" '
                       'stroke-width="1.8"/>' % (f.x(t0 - .01), f.y("f", -16), "#A8442A"))
    f.callout(f.x(1.75), f.y("f", -58), "still flowing out when the next breath starts",
              to=(f.x(3.19), f.y("f", -16)), colour="#A8442A", size=11.5)
    return f.svg()


# -------------------------------------------------------------- 8. mean airway P
def mean_airway():
    f = Fig("Mean airway pressure is the area under the pressure curve, not the height of the peak",
            tmax=6.0, width=680)
    f.add_panel("p", "Pressure", -2, 36, h=150)
    pts = []
    for b in range(3):
        t0 = b * 2.0
        for t, p, fl, v in sample(pc_breath, t0, 2.0, n=120, ti=TI, pset=15, peep=PEEP):
            if t <= f.tmax:
                pts.append((t, p))
    # shade the area under the curve
    area = ['M%.1f %.1f' % (f.x(0), f.y("p", 0))]
    for t, p in pts:
        area.append('L%.1f %.1f' % (f.x(t), f.y("p", p)))
    area.append('L%.1f %.1f Z' % (f.x(pts[-1][0]), f.y("p", 0)))
    f.parts.append('<path d="%s" fill="#A8442A" fill-opacity="0.10" stroke="none"/>' % " ".join(area))
    f.path("p", pts, PRESS)
    f.hline("p", 20, RULE)
    f.hline("p", 11.2, "#A8442A", dash="6 4")
    f.axes()
    f.label(f.W - f.RPAD, f.y("p", 20) - 7, "peak inspiratory pressure", size=11.5,
            colour=MUTED, anchor="end", weight=600)
    f.label(f.W - f.RPAD, f.y("p", 11.2) - 7, "mean airway pressure", size=11.5,
            colour=PRESS, anchor="end", weight=600)
    return f.svg()


# --------------------------------------------------------------- 9. breath phases
def phases():
    f = Fig("The four phases of a mechanical breath", tmax=4.0, width=680)
    f.add_panel("p", "Pressure", -4, 34, h=150)
    pts = [(0, PEEP), (0.30, PEEP), (0.42, PEEP - 2.6), (0.5, PEEP + 4)]
    for i in range(1, 36):
        t = 0.5 + 0.8 * i / 35
        pts.append((t, PEEP + 4 + 16 * (1 - math.exp(-(t - 0.5) / 0.30))))
    pts += [(1.3, PEEP + 20), (1.42, PEEP + 20), (1.5, PEEP)]
    for i in range(1, 40):
        t = 1.5 + 2.5 * i / 40
        pts.append((t, PEEP))
    f.path("p", pts, PRESS, w=2.6)
    bands = [(0.30, 0.50, "Trigger", "#E9E5EF"),
             (0.50, 1.30, "Inspiration", "#EFEBF4"),
             (1.30, 1.50, "Cycle", "#E9E5EF"),
             (1.50, 4.00, "Expiration", "#F4F1F8")]
    for a, b, lab, col in bands:
        f.parts.insert(0, '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s"/>'
                       % (f.x(a), f.P("p")["y0"], f.x(b) - f.x(a), f.P("p")["h"], col))
    f.axes(time_axis=False)
    for a, b, lab, col in bands:
        f.label((f.x(a) + f.x(b)) / 2, f.top - 9, lab, size=12,
                   colour=CALL, anchor="middle", weight=600)
        if a > 0.30:
            f.vline("p", a, "#B9AFC9", dash="3 3")
    return f.svg()


# ------------------------------------------------------------- 10. dyssynchrony
def dyssynchrony():
    """Two common dyssynchronies. Built as one strictly time-ordered sequence:
    the earlier version appended overlapping segments and then sorted them,
    which interleaved two breaths into a scribble."""
    f = Fig("Two common dyssynchronies: an effort the ventilator misses, and one breath taken twice",
            tmax=8.0, width=680)
    f.add_panel("p", "Pressure", -5, 30, h=104)
    f.add_panel("f", "Flow", -70, 70, h=104)
    P, F = [(0.0, PEEP)], [(0.0, 0.0)]

    def hold(t, p, fl):
        P.append((t, p)); F.append((t, fl))

    def supported(t0, ti, pres=13, pk=56):
        """A patient-triggered, pressure-supported breath."""
        hold(t0, PEEP, 0)
        hold(t0 + .08, PEEP - 2.4, -8)                 # the effort
        hold(t0 + .14, PEEP + pres, pk)                # ventilator responds
        for i in range(1, 26):
            t = t0 + .14 + ti * i / 25
            hold(t, PEEP + pres, pk * math.exp(-(t - t0 - .14) / .36))
        tc = t0 + .14 + ti
        hold(tc, PEEP + pres, pk * math.exp(-ti / .36))
        hold(tc + .04, PEEP, -52)                      # cycled off
        return tc + .04

    def expire(t0, t_end, f0=-52):
        for i in range(1, 31):
            t = t0 + (t_end - t0) * i / 30
            hold(t, PEEP, f0 * math.exp(-(t - t0) / .40))

    # 1. an ordinary supported breath
    t = supported(0.35, 0.80); expire(t, 1.95)
    # 2. an effort the ventilator does not see: pressure dents, flow notches, nothing is delivered
    hold(2.00, PEEP, -6)
    hold(2.12, PEEP - 2.0, -15)
    hold(2.26, PEEP - 0.6, -7)
    hold(2.45, PEEP, -4)
    expire(2.45, 3.15, f0=-4)
    # 3. another ordinary breath
    t = supported(3.25, 0.80); expire(t, 5.25)
    # 4. double trigger: the breath cycles off while the effort is still running,
    #    so the ventilator is triggered straight back on
    t = supported(5.40, 0.38)
    hold(t + .02, PEEP + 1, -20)
    hold(t + .08, PEEP + 13, 54)
    for i in range(1, 26):
        tt = t + .08 + .62 * i / 25
        hold(tt, PEEP + 13, 54 * math.exp(-(tt - t - .08) / .36))
    t2 = t + .70
    hold(t2, PEEP + 13, 54 * math.exp(-.62 / .36))
    hold(t2 + .04, PEEP, -56)
    expire(t2 + .04, 8.0, f0=-56)

    assert all(P[i][0] <= P[i + 1][0] for i in range(len(P) - 1)), "pressure trace is out of order"
    assert all(F[i][0] <= F[i + 1][0] for i in range(len(F) - 1)), "flow trace is out of order"
    f.path("p", [q for q in P if q[0] <= f.tmax], PRESS)
    f.path("f", [q for q in F if q[0] <= f.tmax], FLOW)
    f.axes()
    f.legend([(PRESS, "Pressure"), (FLOW, "Flow")])
    f.callout(f.x(1.75), f.y("p", 26), "effort, no breath", anchor="start",
              size=11.5, colour="#A8442A", to=(f.x(2.12), f.y("p", PEEP - 2.0)))
    f.callout(f.x(5.25), f.y("p", 26), "one effort, two breaths", anchor="start",
              size=11.5, colour="#A8442A")
    return f.svg()


# ------------------------------------------------------------- 11. the circuit
def circuit():
    """A schematic of the gas path, drawn from the component list rather than
    copied: source, blender, inspiratory valve, humidifier, patient, expiratory
    (PEEP) valve, filters and sensors, back to atmosphere."""
    W, H = 680, 300
    p = []
    box = ('<rect x="%.0f" y="%.0f" width="%.0f" height="%.0f" rx="6" fill="#fff" '
           'stroke="%s" stroke-width="1.6"/>')
    txt = ('<text x="%.0f" y="%.0f" font-family="' + "'Helvetica Neue',Arial,sans-serif" +
           '" font-size="12" font-weight="600" fill="%s" text-anchor="middle">%s</text>')
    pipe = '<path d="%s" fill="none" stroke="#8E8299" stroke-width="3.2" stroke-linecap="round"/>'
    arrow = ('<path d="M%.0f %.0f l-7 -4 l0 8 Z" fill="#8E8299"/>')

    # inspiratory limb, left to right along the top
    p.append(pipe % "M86 86 L196 86")
    p.append(pipe % "M266 86 L330 86")
    p.append(pipe % "M400 86 L470 86 Q520 86 520 128 L520 150")
    p.append(box % (26, 64, 60, 44, "#8E8299")); p.append(txt % (56, 82, "#473C56", "Gas"))
    p.append(txt % (56, 97, "#473C56", "source"))
    p.append(box % (196, 64, 70, 44, "#8E8299")); p.append(txt % (231, 82, "#473C56", "Inspiratory"))
    p.append(txt % (231, 97, "#473C56", "valve"))
    p.append(box % (330, 64, 70, 44, "#8E8299")); p.append(txt % (365, 82, "#473C56", "Humidifier"))
    p.append(arrow % (170, 86)); p.append(arrow % (316, 86)); p.append(arrow % (452, 86))

    # the patient
    p.append('<path d="M520 150 L520 168" fill="none" stroke="#8E8299" stroke-width="3.2"/>')
    p.append('<ellipse cx="520" cy="200" rx="46" ry="32" fill="#F1EEF6" stroke="#8E8299" '
             'stroke-width="1.6"/>')
    p.append(txt % (520, 205, "#473C56", "Patient"))

    # expiratory limb, right to left along the bottom
    p.append(pipe % "M520 232 L520 254 Q520 266 506 266 L400 266")
    p.append(pipe % "M330 266 L266 266")
    p.append(pipe % "M196 266 L86 266")
    p.append(box % (330, 244, 70, 44, "#8E8299")); p.append(txt % (365, 262, "#473C56", "Expiratory"))
    p.append(txt % (365, 277, "#473C56", "(PEEP) valve"))
    p.append(box % (196, 244, 70, 44, "#8E8299")); p.append(txt % (231, 262, "#473C56", "Filters and"))
    p.append(txt % (231, 277, "#473C56", "sensors"))
    p.append(arrow % (424, 266)); p.append(arrow % (300, 266)); p.append(arrow % (150, 266))
    p.append('<text x="60" y="262" font-family="' + "'Helvetica Neue',Arial,sans-serif" +
             '" font-size="12" font-weight="600" fill="#6B6473" text-anchor="middle">to air</text>')

    p.append('<text x="26" y="24" font-family="' + "'Helvetica Neue',Arial,sans-serif" +
             '" font-size="12.5" font-weight="600" fill="#6B6473">Inspiratory limb</text>')
    p.append('<text x="26" y="300" font-family="' + "'Helvetica Neue',Arial,sans-serif" +
             '" font-size="12.5" font-weight="600" fill="#6B6473">Expiratory limb</text>')
    title = "The ventilator circuit: the path taken by the gas"
    return ('<svg viewBox="0 0 %d %d" width="100%%" '
            'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="%s">\n<title>%s</title>\n%s\n</svg>'
            % (W, H + 6, title, title, "\n".join(p)))


FIGURES = {
    "circuit": circuit,
    "mean-airway": mean_airway,
    "phases": phases,
    "dyssynchrony": dyssynchrony,
    "pressure-control": pressure_control,
    "volume-control": volume_control,
    "pressure-support": pressure_support,
    "simv": simv,
    "pressure-anatomy": pressure_anatomy,
    "resistance": resistance,
    "compliance": compliance,
    "gas-trapping": gas_trapping,
}

if __name__ == "__main__":
    import os
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    for name, fn in FIGURES.items():
        s = fn()
        open(os.path.join(out, name + ".svg"), "w", encoding="utf-8").write(s)
        print("%-20s %6d bytes" % (name, len(s)))
