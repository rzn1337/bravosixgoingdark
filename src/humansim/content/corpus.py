from __future__ import annotations

import os
import sys

# Embedded fallback so content generation works even with no asset files
# present (e.g. a pip-installed copy). Neutral, original filler prose.
FALLBACK_CORPUS = """
The morning started quietly and I spent the first hour reviewing notes from
the previous week. There were a few loose threads to tie up before the team
sync, so I sorted them by priority and made a short plan. Most of the work was
straightforward once I broke it into smaller steps. I find that writing things
down helps me think, even when the ideas are still rough.

After lunch I moved on to the longer task. It needed a bit of research first,
so I gathered a handful of references and skimmed each one for the parts that
mattered. Progress was steady rather than fast. I paused a couple of times to
stretch and to jot down questions for later. By the end of the afternoon the
outline felt solid and I was ready to start drafting.

In the evening I looked back over the day and noted what went well and what I
would change. The main lesson was to start with the hardest part while my
attention was fresh. Small wins add up, and keeping a simple log makes it
easier to pick up the thread tomorrow. I closed the laptop feeling that the
day had been useful, if unremarkable.

Ideas rarely arrive fully formed. They come in pieces, and the trick is to
capture them before they slip away. A quick note now saves a long search
later. When I keep my folders tidy and my notes short, everything moves a
little more smoothly. That is the habit I want to build, one ordinary day at a
time.
""".strip()


def _find_corpus_dir(start: str) -> str | None:
    """Walk up from ``start`` looking for an assets/corpus directory."""
    cur = os.path.abspath(start)
    for _ in range(6):
        candidate = os.path.join(cur, "assets", "corpus")
        if os.path.isdir(candidate):
            return candidate
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent
    return None


def _bundled_corpus_dir() -> str | None:
    """Corpus dir inside a PyInstaller onefile bundle, if present."""
    base = getattr(sys, "_MEIPASS", None)
    if base:
        candidate = os.path.join(base, "assets", "corpus")
        if os.path.isdir(candidate):
            return candidate
    return None


def load_corpus_text() -> str:
    """Combine the embedded fallback with any .txt files under assets/corpus."""
    parts = [FALLBACK_CORPUS]
    corpus_dir = _bundled_corpus_dir() or _find_corpus_dir(os.path.dirname(__file__))
    if corpus_dir:
        for name in sorted(os.listdir(corpus_dir)):
            if name.lower().endswith(".txt"):
                try:
                    with open(
                        os.path.join(corpus_dir, name), "r", encoding="utf-8-sig"
                    ) as fh:
                        parts.append(fh.read())
                except OSError:
                    pass
    return "\n\n".join(p for p in parts if p.strip())
