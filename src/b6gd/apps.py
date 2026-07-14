from __future__ import annotations

import os
import shutil
import subprocess
import sys

from .platform_detect import PlatformInfo

_LINUX_EDITORS = ["gnome-text-editor", "gedit", "kate", "mousepad", "xed", "leafpad"]
_LINUX_FILES = ["nautilus", "nemo", "dolphin", "thunar", "pcmanfm", "caja"]
_LINUX_TERMINALS = [
    "gnome-terminal",
    "konsole",
    "xfce4-terminal",
    "mate-terminal",
    "tilix",
    "kitty",
    "alacritty",
    "x-terminal-emulator",
    "xterm",
]


def find_editor(info: PlatformInfo, override: str = "") -> str:
    if override:
        return override
    if info.is_windows:
        return "notepad.exe"
    if info.is_mac:
        return "TextEdit"
    for cand in _LINUX_EDITORS:
        if shutil.which(cand):
            return cand
    return ""


def find_filemanager(info: PlatformInfo, override: str = "") -> str:
    if override:
        return override
    if info.is_windows:
        return "explorer.exe"
    if info.is_mac:
        return "open"
    for cand in _LINUX_FILES:
        if shutil.which(cand):
            return cand
    return "xdg-open"


def find_terminal(info: PlatformInfo, override: str = "") -> str:
    if override:
        return override
    if info.is_windows:
        return "cmd.exe"
    if info.is_mac:
        return "Terminal"
    for cand in _LINUX_TERMINALS:
        if shutil.which(cand):
            return cand
    return ""


class Apps:
    """Discovers and launches the notes editor and file manager per OS, and
    supplies window-title hints so the focus guard can confirm the right app
    is in front before we type."""

    def __init__(self, info: PlatformInfo, settings, logger, dry_run: bool = False) -> None:
        self.info = info
        self.log = logger
        self.dry_run = dry_run
        self.editor = find_editor(info, settings.editor_cmd)
        self.filemanager = find_filemanager(info, settings.filemanager_cmd)
        self.terminal = find_terminal(info, settings.terminal_cmd)

    # ---- launch -------------------------------------------------------
    @staticmethod
    def _child_env():
        """Environment for launched system apps. In a PyInstaller onefile build,
        LD_LIBRARY_PATH points at the bundle's temp dir, so child processes load
        our bundled libraries (e.g. an older libcrypto) instead of the system
        ones — which breaks apps like gnome-text-editor / nautilus. Restore the
        original pre-bundle value so system apps launch correctly."""
        env = dict(os.environ)
        if getattr(sys, "frozen", False):
            for var in ("LD_LIBRARY_PATH", "DYLD_LIBRARY_PATH"):
                orig = env.get(var + "_ORIG")
                if orig is not None:
                    env[var] = orig
                else:
                    env.pop(var, None)
        return env

    def _popen(self, cmd):
        try:
            return subprocess.Popen(
                cmd,
                env=self._child_env(),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,  # detach: our Ctrl+C won't hit the child
            )
        except Exception as exc:
            self.log.warning("Failed to launch %s: %s", cmd, exc)
            return None

    def launch_editor(self, filepath: str | None = None):
        if self.dry_run:
            where = f" on {filepath}" if filepath else " (blank document)"
            self.log.info("[dry] would launch editor %s%s", self.editor, where)
            return None
        if self.info.is_windows:
            cmd = [self.editor or "notepad.exe"]
        elif self.info.is_mac:
            cmd = ["open", "-a", self.editor or "TextEdit"]
        elif not self.editor:
            self.log.warning(
                "No text editor found. Install one of: %s", ", ".join(_LINUX_EDITORS)
            )
            return None
        else:
            cmd = [self.editor]
        if filepath:
            cmd.append(filepath)
        return self._popen(cmd)

    def launch_filemanager(self, path: str):
        if self.dry_run:
            self.log.info("[dry] would launch file manager %s at %s", self.filemanager, path)
            return None
        if self.info.is_windows:
            return self._popen(["explorer.exe", path])
        if self.info.is_mac:
            return self._popen(["open", path])
        return self._popen([self.filemanager or "xdg-open", path])

    def launch_browser(self, url: str):
        if self.dry_run:
            self.log.info("[dry] would open browser at %s", url)
            return None
        if self.info.is_windows:
            return self._popen(["cmd", "/c", "start", "", url])
        if self.info.is_mac:
            return self._popen(["open", url])
        return self._popen(["xdg-open", url])

    def launch_terminal(self):
        if self.dry_run:
            self.log.info("[dry] would open a terminal (%s)", self.terminal or "default")
            return None
        if self.info.is_windows:
            # A new, interactive console window we can type into.
            return self._popen(["cmd", "/c", "start", "", "cmd"])
        if self.info.is_mac:
            return self._popen(["open", "-a", "Terminal"])
        if not self.terminal:
            self.log.warning(
                "No terminal emulator found. Install one of: %s",
                ", ".join(_LINUX_TERMINALS),
            )
            return None
        return self._popen([self.terminal])

    def launch_terminal_run(self, posix_script: str, windows_script: str):
        """Open a terminal that RUNS ``script`` and closes when it finishes.
        Unlike typing into a terminal (which needs keyboard focus we can't get on
        Wayland), the commands actually run in the new window with no focus."""
        if self.dry_run:
            self.log.info("[dry] would open a terminal running: %s", posix_script)
            return None
        if self.info.is_windows:
            return self._popen(["cmd", "/c", "start", "", "cmd", "/c", windows_script])
        if self.info.is_mac:
            script = posix_script.replace("\\", "\\\\").replace('"', '\\"')
            return self._popen(
                ["osascript", "-e", f'tell application "Terminal" to do script "{script}"']
            )
        term = self.terminal
        if not term:
            self.log.warning(
                "No terminal emulator found. Install one of: %s",
                ", ".join(_LINUX_TERMINALS),
            )
            return None
        inner = ["bash", "-c", posix_script]
        base = os.path.basename(term)
        if base in ("gnome-terminal", "mate-terminal", "tilix"):
            argv = [term, "--", *inner]
        elif base == "xfce4-terminal":
            argv = [term, "-x", *inner]
        elif base == "kitty":
            argv = [term, *inner]
        else:  # konsole, xterm, x-terminal-emulator, alacritty, and fallback
            argv = [term, "-e", *inner]
        return self._popen(argv)

    # ---- focus hints --------------------------------------------------
    def editor_title_hints(self, filepath: str | None = None):
        hints = []
        if filepath:
            hints.append(os.path.splitext(os.path.basename(filepath))[0])
        if self.info.is_windows:
            hints += ["Notepad", "Untitled"]
        elif self.info.is_mac:
            hints += ["TextEdit"]
        else:
            hints += ["Text Editor", "gedit", "kate", "mousepad", "Editor"]
            if self.editor:
                hints.append(os.path.basename(self.editor))
        return [h for h in hints if h]

    def filemanager_title_hints(self):
        if self.info.is_windows:
            return ["File Explorer", "Explorer", "B6GDWorkspace"]
        if self.info.is_mac:
            return ["Finder"]
        return ["Files", "Nautilus", "Nemo", "Dolphin", "Thunar", "B6GDWorkspace"]

    def browser_title_hints(self):
        return [
            "YouTube",
            "Chrome",
            "Firefox",
            "Edge",
            "Mozilla",
            "Chromium",
            "Brave",
            "Opera",
        ]

    def terminal_title_hints(self):
        if self.info.is_windows:
            return ["cmd", "Command Prompt", "PowerShell", "Terminal"]
        if self.info.is_mac:
            return ["Terminal"]
        return ["Terminal", "gnome-terminal", "Konsole", "xterm", "bash", "zsh"]
