from .base import Activity
from .browse_folders import BrowseFolders
from .idle import IdleWander
from .random_click import RandomClick
from .switch_windows import SwitchWindows
from .terminal_work import TerminalWork
from .watch_video import WatchVideo
from .write_note import WriteNote

REGISTRY = {
    cls.name: cls
    for cls in (
        WriteNote,
        BrowseFolders,
        IdleWander,
        SwitchWindows,
        WatchVideo,
        RandomClick,
        TerminalWork,
    )
}

__all__ = [
    "Activity",
    "WriteNote",
    "BrowseFolders",
    "IdleWander",
    "SwitchWindows",
    "WatchVideo",
    "RandomClick",
    "TerminalWork",
    "REGISTRY",
]
