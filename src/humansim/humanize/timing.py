from __future__ import annotations

import random


def jitter(value: float, frac: float = 0.2, rng=None) -> float:
    """``value`` perturbed by +/- up to ``frac`` (uniform)."""
    rng = rng or random
    return value * (1.0 + rng.uniform(-frac, frac))


def human_pause(mean: float = 1.0, spread: float = 0.5, rng=None) -> float:
    """A positive, right-skewed pause (log-normal-ish) around ``mean`` seconds."""
    rng = rng or random
    val = rng.lognormvariate(0.0, spread) * mean
    return max(0.05, min(val, mean * 6.0))


def think_pause(lo: float = 0.4, hi: float = 1.8, rng=None) -> float:
    rng = rng or random
    return rng.uniform(lo, hi)
