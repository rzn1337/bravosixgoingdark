from __future__ import annotations

import os
import shutil
import subprocess
import sys

from .platform_detect import PlatformInfo

_LINUX_EDITORS = ["gnome-text-editor", "gedit", "kate", "mousepad", "xed", "leafpad"]
_LINUX_FILES = ["nautilus", "nemo", "dolphin", "thunar", "pcmanfm", "caja"]


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
            return subprocess.Popen(cmd, env=self._child_env())
        except Exception as exc:
            self.log.warning("Failed to launch %s: %s", cmd, exc)
            return None

    def launch_editor(self, filepath: str):
        if self.dry_run:
            self.log.info("[dry] would launch editor %s on %s", self.editor, filepath)
            return None
        if self.info.is_windows:
            return self._popen([self.editor or "notepad.exe", filepath])
        if self.info.is_mac:
            return self._popen(["open", "-a", self.editor or "TextEdit", filepath])
        if not self.editor:
            self.log.warning(
                "No text editor found. Install one of: %s", ", ".join(_LINUX_EDITORS)
            )
            return None
        return self._popen([self.editor, filepath])

    def launch_filemanager(self, path: str):
        if self.dry_run:
            self.log.info("[dry] would launch file manager %s at %s", self.filemanager, path)
            return None
        if self.info.is_windows:
            return self._popen(["explorer.exe", path])
        if self.info.is_mac:
            return self._popen(["open", path])
        return self._popen([self.filemanager or "xdg-open", path])

    # ---- focus hints --------------------------------------------------
    def editor_title_hints(self, filepath: str):
        stem = os.path.splitext(os.path.basename(filepath))[0]
        hints = [stem]
        if self.info.is_windows:
            hints += ["Notepad"]
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
