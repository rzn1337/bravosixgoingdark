from __future__ import annotations

import random


class Markov:
    """A tiny word-level Markov chain (pure Python, no deps). Order-2 by
    default; degrades gracefully on small corpora."""

    def __init__(self, order: int = 2, rng=None) -> None:
        self.order = max(1, order)
        self.rng = rng or random
        self.trans: dict[tuple, list] = {}
        self.starts: list[tuple] = []

    def train(self, text: str) -> None:
        tokens = text.split()
        o = self.order
        if len(tokens) <= o:
            return
        for i in range(len(tokens) - o):
            key = tuple(tokens[i : i + o])
            self.trans.setdefault(key, []).append(tokens[i + o])
            if i == 0 or tokens[i - 1][-1:] in ".!?":
                first = tokens[i]
                if first[:1].isupper():
                    self.starts.append(key)
        if not self.starts:
            self.starts.append(tuple(tokens[:o]))

    def ready(self) -> bool:
        return bool(self.starts)

    def sentence(self, max_words: int = 22) -> str:
        if not self.starts:
            return ""
        out = list(self.rng.choice(self.starts))
        while len(out) < max_words:
            nxt = self.trans.get(tuple(out[-self.order :]))
            if not nxt:
                break
            word = self.rng.choice(nxt)
            out.append(word)
            if word[-1:] in ".!?":
                break
        s = " ".join(out).strip()
        if s and s[-1] not in ".!?":
            s = s.rstrip(",;:") + "."
        return s[:1].upper() + s[1:] if s else s

    def paragraph(self, sentences: int = 3, max_words: int = 22) -> str:
        return " ".join(self.sentence(max_words) for _ in range(sentences)).strip()

    def phrase(self, words: int = 4) -> str:
        """A short lowercase fragment for list items / headings."""
        s = self.sentence(max_words=words + self.order)
        s = s.rstrip(".!?")
        parts = s.split()
        return " ".join(parts[:words]).lower() if parts else "note"
