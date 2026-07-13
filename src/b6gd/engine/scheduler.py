from __future__ import annotations

import random


class Scheduler:
    """Picks the next activity. Two modes (``settings.schedule.order``):

    - ``shuffle`` (default): a shuffle bag — every enabled activity runs once
      per round in a random order, so all actions occur equally often but never
      in a fixed sequence. Avoids back-to-back repeats across round boundaries.
    - ``weighted``: weighted-random by ``activity_weights`` with a mild
      anti-repeat penalty.
    """

    def __init__(self, settings, available_names, rng=None) -> None:
        self.s = settings
        self.rng = rng or random
        self.names = list(available_names)
        self.mode = getattr(settings.schedule, "order", "shuffle")
        self.weights = {
            n: max(0.0, float(settings.activity_weights.get(n, 1.0)))
            for n in self.names
        }
        self._bag = []

    def next_activity(self, last: str | None) -> str | None:
        if not self.names:
            return None
        if len(self.names) == 1:
            return self.names[0]
        if self.mode == "shuffle":
            return self._next_shuffle(last)
        return self._next_weighted(last)

    def _next_shuffle(self, last: str | None) -> str:
        if not self._bag:
            self._bag = list(self.names)
            self.rng.shuffle(self._bag)
            # Avoid the same activity twice in a row across a round boundary.
            if last is not None and len(self._bag) > 1 and self._bag[0] == last:
                self._bag[0], self._bag[1] = self._bag[1], self._bag[0]
        return self._bag.pop(0)

    def _next_weighted(self, last: str | None) -> str:
        weights = [self.weights[n] for n in self.names]
        if last in self.names:
            weights[self.names.index(last)] *= self.s.schedule.repeat_penalty
        total = sum(weights)
        if total <= 0:
            return self.rng.choice(self.names)
        r = self.rng.uniform(0.0, total)
        acc = 0.0
        for name, w in zip(self.names, weights):
            acc += w
            if r <= acc:
                return name
        return self.names[-1]
