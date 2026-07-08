from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Context:
    """Everything an activity needs, assembled once by the session."""

    info: Any
    settings: Any
    control: Any
    backend: Any
    exe: Any
    sandbox: Any
    apps: Any
    focus: Any
    content: Any
    log: Any
    rng: Any
    screen_size: tuple
    tracked: list = field(default_factory=list)
