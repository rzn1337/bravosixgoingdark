from __future__ import annotations

from .base import Activity


class BrowseFolders(Activity):
    """Open the file manager at the sandbox root and move around it — hovering,
    occasionally double-clicking to open a folder, scrolling, and going back.
    Stays within the sandbox; double-clicking empty space is harmless."""

    name = "browse"

    def run(self) -> None:
        ctx = self.ctx
        rng = ctx.rng

        root = ctx.sandbox.root
        ctx.log.info(
            "browse: opening file manager (%s) at %s",
            ctx.apps.filemanager or "default",
            root,
        )
        proc = ctx.apps.launch_filemanager(root)
        if proc is not None:
            ctx.tracked.append(proc)

        if not ctx.exe.wait(rng.uniform(1.5, 3.0)):
            return

        w, h = ctx.screen_size
        for _ in range(rng.randint(2, 4)):
            if ctx.control.stopped():
                return
            x = rng.randint(int(w * 0.18), int(w * 0.55))
            y = rng.randint(int(h * 0.25), int(h * 0.70))
            ctx.log.info("browse: look around (%d, %d)", x, y)
            if not ctx.exe.move_to(x, y):
                return
            if rng.random() < 0.5:
                ctx.exe.double_click()
                ctx.exe.wait(rng.uniform(0.8, 1.8))
            if rng.random() < 0.6:
                ctx.exe.scroll(rng.choice([-4, -3, 3, 4]))
                ctx.exe.wait(rng.uniform(0.4, 1.2))
            if rng.random() < 0.5:
                ctx.log.info("browse: back")
                ctx.exe.hotkey("alt", "left")
            if not ctx.exe.wait(rng.uniform(0.6, 1.8)):
                return
