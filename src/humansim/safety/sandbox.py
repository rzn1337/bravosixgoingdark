from __future__ import annotations

import os
from datetime import datetime


class Sandbox:
    """A dedicated workspace that is the ONLY place activities read, write, or
    navigate. Never touches real user files.
    """

    SUBDIRS = ["Notes", "Documents", "Projects", "Reference", "Archive"]

    def __init__(self, root: str) -> None:
        self.root = os.path.abspath(root)

    def ensure(self) -> None:
        os.makedirs(self.root, exist_ok=True)
        for d in self.SUBDIRS:
            os.makedirs(os.path.join(self.root, d), exist_ok=True)
        self._seed()

    def _seed(self) -> None:
        seeds = {
            "README.txt": (
                "HumanSim workspace\n"
                "==================\n\n"
                "This folder is a sandbox. HumanSim only ever opens, types into,\n"
                "and browses files *inside here* — never your real documents.\n"
                "It is safe to delete; it will be recreated on the next run.\n"
            ),
            os.path.join("Documents", "welcome.txt"): (
                "Welcome notes\n-------------\nPlaceholder document used for browsing.\n"
            ),
            os.path.join("Projects", "todo.txt"): (
                "Project TODO\n------------\n[ ] draft outline\n[ ] review notes\n[ ] follow up\n"
            ),
            os.path.join("Reference", "links.txt"): (
                "Reference\n---------\nAssorted reference material lives here.\n"
            ),
            os.path.join("Archive", "old_notes.txt"): (
                "Archive\n-------\nOlder notes are kept here for reference.\n"
            ),
        }
        for rel, content in seeds.items():
            path = os.path.join(self.root, rel)
            if not os.path.exists(path):
                try:
                    with open(path, "w", encoding="utf-8") as fh:
                        fh.write(content)
                except OSError:
                    pass

    def new_note_path(self) -> str:
        """Create (touch) and return the path to a fresh, empty note file so
        the editor opens it in place and Ctrl+S saves without a dialog."""
        stamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        path = os.path.join(self.root, "Notes", f"note_{stamp}.txt")
        try:
            open(path, "a", encoding="utf-8").close()
        except OSError:
            pass
        return path

    def pick_existing_file(self) -> str | None:
        for base, _dirs, files in os.walk(self.root):
            for name in files:
                if name.lower().endswith((".txt", ".md")):
                    return os.path.join(base, name)
        return None

    def contains(self, path: str) -> bool:
        try:
            return (
                os.path.commonpath([self.root, os.path.abspath(path)]) == self.root
            )
        except ValueError:
            return False
