from __future__ import annotations

import shutil

from ..platform_detect import PlatformInfo
from .base import InputBackend

WAYLAND_MESSAGE = (
    "You're on a Wayland session, which blocks normal synthetic input for "
    "security.\nHumanSim needs one of:\n"
    "  1. Install ydotool and run its daemon:\n"
    "       sudo apt install ydotool\n"
    "       sudo systemctl enable --now ydotool    # or: sudo ydotoold &\n"
    "     (you may need udev permissions on /dev/uinput — see the README), or\n"
    "  2. Log out and pick 'Ubuntu on Xorg' at the login screen (gear icon),\n"
    "     which needs no extra setup.\n"
    "Tip: run `python run.py doctor` to re-check."
)


class BackendUnavailable(RuntimeError):
    pass


def make_backend(
    info: PlatformInfo, dry_run: bool = False
) -> InputBackend:
    if dry_run:
        from .dryrun_backend import DryRunBackend

        return DryRunBackend(info)

    if info.is_wayland:
        if shutil.which("ydotool"):
            from .ydotool_backend import YdotoolBackend

            return YdotoolBackend(info)
        raise BackendUnavailable(WAYLAND_MESSAGE)

    from .pynput_backend import PynputBackend

    return PynputBackend(info)


def describe_backend(info: PlatformInfo) -> str:
    """What backend a real run would use, for `doctor` (no side effects)."""
    if info.is_wayland:
        return "ydotool" if shutil.which("ydotool") else "unavailable (Wayland)"
    if info.is_windows or info.is_mac or info.session_type == "x11":
        return "pynput"
    return "pynput (best-effort; no display server detected)"
