from __future__ import annotations

_UNITS = {"s": 1.0, "m": 60.0, "h": 3600.0}


def parse_duration(text: str) -> float:
    """Parse a human duration like '30m', '1h', '90s', or '45' (bare = seconds).

    Also accepts simple combos like '1h30m' or '2m30s'.
    """
    text = str(text).strip().lower().replace(" ", "")
    if not text:
        raise ValueError("empty duration")

    # Bare number => seconds.
    try:
        return float(text)
    except ValueError:
        pass

    total = 0.0
    num = ""
    matched = False
    for ch in text:
        if ch.isdigit() or ch == ".":
            num += ch
        elif ch in _UNITS:
            if not num:
                raise ValueError(f"bad duration: {text!r}")
            total += float(num) * _UNITS[ch]
            num = ""
            matched = True
        else:
            raise ValueError(f"bad duration: {text!r}")
    if num:  # trailing bare number after a unit => seconds
        total += float(num)
        matched = True
    if not matched:
        raise ValueError(f"bad duration: {text!r}")
    return total


def format_duration(seconds: float) -> str:
    seconds = int(round(seconds))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    parts = []
    if h:
        parts.append(f"{h}h")
    if m:
        parts.append(f"{m}m")
    if s or not parts:
        parts.append(f"{s}s")
    return "".join(parts)
