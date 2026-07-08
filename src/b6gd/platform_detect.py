from __future__ import annotations

import os
import platform
from dataclasses import dataclass


@dataclass(frozen=True)
class PlatformInfo:
    system: str  # "Windows" | "Linux" | "Darwin"
    session_type: str  # "windows" | "x11" | "wayland" | "quartz" | "unknown"
    is_windows: bool
    is_linux: bool
    is_mac: bool

    @property
    def is_wayland(self) -> bool:
        return self.session_type == "wayland"


def detect() -> PlatformInfo:
    system = platform.system()
    is_windows = system == "Windows"
    is_linux = system == "Linux"
    is_mac = system == "Darwin"

    if is_windows:
        session = "windows"
    elif is_mac:
        session = "quartz"
    else:
        session = (os.environ.get("XDG_SESSION_TYPE") or "").lower()
        if session not in ("x11", "wayland"):
            if os.environ.get("WAYLAND_DISPLAY"):
                session = "wayland"
            elif os.environ.get("DISPLAY"):
                session = "x11"
            else:
                session = "unknown"

    return PlatformInfo(
        system=system,
        session_type=session,
        is_windows=is_windows,
        is_linux=is_linux,
        is_mac=is_mac,
    )
