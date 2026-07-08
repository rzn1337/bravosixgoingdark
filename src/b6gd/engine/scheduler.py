from __future__ import annotations

import random


class Scheduler:
    """Weighted-random activity picker with a mild anti-repeat penalty so the
    same activity doesn't fire twice in a row too often. Keeps the sequence
    feeling natural rather than round-robin."""

    def __init__(self, settings, available_names, rng=None) -> None:
        self.s = settings
        self.rng = rng or random
        self.names = list(available_names)
        self.weights = {
            n: max(0.0, float(settings.activity_weights.get(n, 1.0)))
            for n in self.names
        }

    def next_activity(self, last: str | None) -> str | None:
        if not self.names:
            return None
        if len(self.names) == 1:
            return self.names[0]

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
