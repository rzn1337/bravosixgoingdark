from __future__ import annotations

import math
import random


def _bezier(p0, p1, p2, p3, t):
    mt = 1.0 - t
    a, b, c, d = mt * mt * mt, 3 * mt * mt * t, 3 * mt * t * t, t * t * t
    return (
        a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0],
        a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1],
    )


def _ease(t: float) -> float:
    """Smoothstep ease-in/ease-out in [0, 1]."""
    return t * t * (3.0 - 2.0 * t)


def plan_move(start, end, cfg, rng=None):
    """Return a list of (x, y, dt) waypoints from ``start`` to ``end``.

    The path is a cubic Bézier (curved, not a straight line); positions are
    sampled along an eased progress so the cursor accelerates then decelerates;
    small gaussian tremor is added; and with some probability it overshoots the
    target and corrects back. The final waypoint is exactly ``end``.
    ``dt`` is the delay (seconds) to wait *before* moving to that point.
    """
    rng = rng or random
    sx, sy = float(start[0]), float(start[1])
    ex, ey = float(end[0]), float(end[1])
    dist = math.hypot(ex - sx, ey - sy)
    if dist < 2.0:
        return [(int(round(ex)), int(round(ey)), 0.0)]

    span = cfg.max_duration_s - cfg.min_duration_s
    dur = (cfg.min_duration_s + span * min(1.0, dist / 1200.0)) * rng.uniform(0.85, 1.15)

    steps = int(cfg.steps_per_100px * dist / 100.0)
    steps = max(8, min(steps, 120))

    do_overshoot = rng.random() < cfg.overshoot_chance and dist > 150.0
    if do_overshoot:
        frac = rng.uniform(0.03, 0.09)
        ux, uy = (ex - sx) / dist, (ey - sy) / dist
        tx, ty = ex + ux * dist * frac, ey + uy * dist * frac
    else:
        tx, ty = ex, ey

    dx, dy = tx - sx, ty - sy
    plen = math.hypot(dx, dy) or 1.0
    perp = (-dy / plen, dx / plen)
    offset = cfg.curvature * dist * rng.uniform(-1.0, 1.0)
    c1 = (sx + dx * 0.3 + perp[0] * offset, sy + dy * 0.3 + perp[1] * offset)
    c2 = (sx + dx * 0.7 + perp[0] * offset, sy + dy * 0.7 + perp[1] * offset)

    dt = dur / steps
    pts = []
    for i in range(1, steps + 1):
        t = _ease(i / steps)
        x, y = _bezier((sx, sy), c1, c2, (tx, ty), t)
        if i < steps:
            x += rng.gauss(0.0, cfg.tremor_px)
            y += rng.gauss(0.0, cfg.tremor_px)
        pts.append((int(round(x)), int(round(y)), dt))

    if do_overshoot:
        settle = max(3, steps // 8)
        sdt = 0.14 / settle
        lx, ly = tx, ty
        for j in range(1, settle + 1):
            t = _ease(j / settle)
            pts.append(
                (int(round(lx + (ex - lx) * t)), int(round(ly + (ey - ly) * t)), sdt)
            )

    # Land exactly on target.
    lastx, lasty, lastdt = pts[-1]
    pts[-1] = (int(round(ex)), int(round(ey)), lastdt)
    return pts


def random_point(rect, rng=None):
    """A random (x, y) inside ``rect`` = (left, top, right, bottom)."""
    rng = rng or random
    left, top, right, bottom = rect
    return (rng.randint(int(left), int(right)), rng.randint(int(top), int(bottom)))


def screen_rect(size, margin=0.08):
    """An inset rectangle of the screen so the cursor stays away from edges."""
    w, h = size
    mx, my = int(w * margin), int(h * margin)
    return (mx, my, w - mx, h - my)
