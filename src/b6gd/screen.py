from __future__ import annotations

from .platform_detect import PlatformInfo

_FALLBACK = (1920, 1080)


def get_screen_size(info: PlatformInfo) -> tuple[int, int]:
    """Best-effort primary screen size in pixels. Uses only stdlib / the
    python-xlib that ships with pynput on Linux. Never raises."""
    try:
        if info.is_windows:
            import ctypes

            user32 = ctypes.windll.user32
            try:
                user32.SetProcessDPIAware()
            except Exception:
                pass
            w = int(user32.GetSystemMetrics(0))
            h = int(user32.GetSystemMetrics(1))
            if w > 0 and h > 0:
                return w, h

        elif info.is_linux:
            # Prefer Xlib (dependency of pynput on X11); harmless on Wayland Xwayland.
            try:
                from Xlib import display  # type: ignore

                d = display.Display()
                s = d.screen()
                w, h = int(s.width_in_pixels), int(s.height_in_pixels)
                d.close()
                if w > 0 and h > 0:
                    return w, h
            except Exception:
                pass
            # Fall back to xrandr if present.
            try:
                import re
                import subprocess

                out = subprocess.run(
                    ["xrandr"], capture_output=True, text=True, timeout=2
                ).stdout
                m = re.search(r"current (\d+) x (\d+)", out)
                if m:
                    return int(m.group(1)), int(m.group(2))
            except Exception:
                pass

        elif info.is_mac:
            try:
                import Quartz  # type: ignore

                main = Quartz.CGMainDisplayID()
                return (
                    int(Quartz.CGDisplayPixelsWide(main)),
                    int(Quartz.CGDisplayPixelsHigh(main)),
                )
            except Exception:
                pass
    except Exception:
        pass

    return _FALLBACK
