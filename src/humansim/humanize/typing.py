from __future__ import annotations

import random
from dataclasses import dataclass

# Physically adjacent keys on a QWERTY layout (for believable typos).
_QWERTY_ADJ = {
    "q": "wa",
    "w": "qeas",
    "e": "wrsd",
    "r": "etdf",
    "t": "ryfg",
    "y": "tugh",
    "u": "yihj",
    "i": "uojk",
    "o": "ipkl",
    "p": "ol",
    "a": "qwsz",
    "s": "awedxz",
    "d": "serfcx",
    "f": "drtgvc",
    "g": "ftyhbv",
    "h": "gyujnb",
    "j": "huikmn",
    "k": "jiolm",
    "l": "kop",
    "z": "asx",
    "x": "zsdc",
    "c": "xdfv",
    "v": "cfgb",
    "b": "vghn",
    "n": "bhjm",
    "m": "njk",
}

_SENTENCE_ENDERS = ".!?\n"


@dataclass
class TypeEvent:
    kind: str  # "char" | "key"
    value: str  # the character, or a key name like "enter"/"backspace"
    delay: float  # seconds to wait BEFORE emitting this event


def base_delay(wpm: float) -> float:
    """Average seconds per character for a given words-per-minute (5 chars/word)."""
    cps = max(1.0, wpm * 5.0 / 60.0)
    return 1.0 / cps


def plan_typing(text: str, cfg, rng=None):
    """Turn ``text`` into a stream of :class:`TypeEvent` with human timing:
    per-key jitter, longer 'thinking' pauses after sentence/line ends, and
    occasional adjacent-key typos that are usually (but not always) corrected
    with a backspace."""
    rng = rng or random
    base = base_delay(cfg.wpm)
    events: list[TypeEvent] = []

    for i, ch in enumerate(text):
        delay = max(0.02, rng.gauss(base, base * cfg.wpm_jitter))
        if i > 0 and text[i - 1] in _SENTENCE_ENDERS:
            delay += rng.uniform(cfg.think_pause_min_s, cfg.think_pause_max_s)

        low = ch.lower()
        if low in _QWERTY_ADJ and rng.random() < cfg.typo_rate:
            wrong = rng.choice(_QWERTY_ADJ[low])
            if ch.isupper():
                wrong = wrong.upper()
            events.append(TypeEvent("char", wrong, delay))
            if rng.random() >= cfg.uncorrected_typo_fraction:
                events.append(TypeEvent("key", "backspace", rng.uniform(0.15, 0.45)))
                events.append(
                    TypeEvent("char", ch, rng.uniform(base * 0.5, base * 1.2))
                )
            # else: leave the typo uncorrected (skip the intended char).
        elif ch == "\n":
            events.append(TypeEvent("key", "enter", delay))
        else:
            events.append(TypeEvent("char", ch, delay))

    return events


def planned_duration(events) -> float:
    return sum(e.delay for e in events)
