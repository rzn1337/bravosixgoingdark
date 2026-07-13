from __future__ import annotations

from .base import Activity, close_app, focus_window


class BrowseFolders(Activity):
    """Open the file manager at the sandbox root, move around it, then close it so
    long runs don't accumulate file-manager windows."""

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
        focus_window(ctx)

        w, h = ctx.screen_size
        for _ in range(rng.randint(2, 4)):
            if ctx.control.stopped():
                break
            x = rng.randint(int(w * 0.18), int(w * 0.55))
            y = rng.randint(int(h * 0.25), int(h * 0.70))
            ctx.log.info("browse: look around (%d, %d)", x, y)
            if not ctx.exe.move_to(x, y):
                break
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
                break

        close_app(ctx, proc, ctrl_w=True)
