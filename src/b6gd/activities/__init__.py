from .base import Activity
from .browse_folders import BrowseFolders
from .idle import IdleWander
from .switch_windows import SwitchWindows
from .write_note import WriteNote

REGISTRY = {
    cls.name: cls
    for cls in (WriteNote, BrowseFolders, IdleWander, SwitchWindows)
}

__all__ = [
    "Activity",
    "WriteNote",
    "BrowseFolders",
    "IdleWander",
    "SwitchWindows",
    "REGISTRY",
]
