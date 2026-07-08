from __future__ import annotations

import random
from datetime import datetime

KINDS = ["journal", "todo", "meeting", "ideas"]


def _bullets(markov, n, marker="- "):
    return "\n".join(marker + markov.phrase(random.randint(2, 5)) for _ in range(n))


def make_note(markov, rng=None, kind: str | None = None) -> str:
    rng = rng or random
    kind = kind or rng.choice(KINDS)
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M")

    if kind == "journal":
        return (
            f"Journal — {date} {time}\n"
            f"{'=' * 24}\n\n"
            f"{markov.paragraph(sentences=rng.randint(2, 3))}\n\n"
            f"{markov.paragraph(sentences=rng.randint(2, 3))}\n"
        )

    if kind == "todo":
        return (
            f"To-do ({date})\n"
            f"{'-' * 16}\n"
            f"{_bullets(markov, rng.randint(3, 6), '[ ] ')}\n\n"
            f"Notes: {markov.sentence()}\n"
        )

    if kind == "meeting":
        return (
            f"Meeting notes — {date}\n"
            f"{'-' * 20}\n"
            f"Attendees: {markov.phrase(3).title()}, {markov.phrase(2).title()}\n\n"
            f"Discussion:\n{_bullets(markov, rng.randint(2, 4))}\n\n"
            f"Action items:\n{_bullets(markov, rng.randint(2, 3), '-> ')}\n"
        )

    # ideas
    return (
        f"Ideas & scratch — {date} {time}\n"
        f"{'~' * 26}\n\n"
        f"{markov.sentence()}\n\n"
        f"Maybe:\n{_bullets(markov, rng.randint(2, 4), '* ')}\n"
    )
