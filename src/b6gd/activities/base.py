from __future__ import annotations

from ..engine.context import Context


class Activity:
    name = "base"

    def __init__(self, ctx: Context) -> None:
        self.ctx = ctx

    def run(self) -> None:
        raise NotImplementedError
