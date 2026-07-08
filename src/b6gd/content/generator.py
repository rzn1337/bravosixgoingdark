from __future__ import annotations

import random

from .corpus import load_corpus_text
from .markov import Markov
from .templates import KINDS, make_note


class ContentGen:
    """Offline note generator: builds a Markov model from the bundled corpus
    and renders structured notes. Fully local, no network."""

    def __init__(self, rng=None) -> None:
        self.rng = rng or random
        self.markov = Markov(order=2, rng=self.rng)
        self.markov.train(load_corpus_text())

    def make_note(self, kind: str | None = None) -> str:
        return make_note(self.markov, self.rng, kind)

    @property
    def kinds(self):
        return list(KINDS)
