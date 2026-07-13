from __future__ import annotations

from .base import Activity, close_app, focus_window


class WriteNote(Activity):
    """Open the notes editor on a blank document and type a generated note with
    human rhythm. It never saves, and it closes the editor afterwards so long
    runs don't pile up windows."""

    name = "write"

    def run(self) -> None:
        ctx = self.ctx
        rng = ctx.rng

        ctx.log.info(
            "write: opening editor (%s), blank document", ctx.apps.editor or "default"
        )
        proc = ctx.apps.launch_editor()  # blank; we never save
        if proc is not None:
            ctx.tracked.append(proc)

        if not ctx.exe.wait(rng.uniform(1.5, 3.0)):  # let the app come up
            return

        hints = ctx.apps.editor_title_hints()
        ctx.focus.activate(hints)  # best-effort raise (Windows / X11)
        focus_window(ctx)  # click-to-focus so keys land in the editor, not the terminal
        if not ctx.exe.wait(rng.uniform(0.3, 0.8)):
            close_app(ctx, proc, ctrl_w=False)
            return

        assume = getattr(ctx.settings, "assume_focus", True)
        if ctx.focus.can_detect():
            if not ctx.focus.wait_for(hints, timeout=6.0) and not assume:
                ctx.log.warning("write: editor not in foreground — skipping typing.")
                close_app(ctx, proc, ctrl_w=False)
                return
        elif not assume:
            ctx.log.warning(
                "write: can't verify window focus and --strict-focus is set — skipping."
            )
            close_app(ctx, proc, ctrl_w=False)
            return

        text = ctx.content.make_note()
        ctx.log.info("write: typing note (%d chars); not saving", len(text))
        ctx.exe.type_text(text)
        ctx.exe.wait(rng.uniform(1.0, 2.5))
        close_app(ctx, proc, ctrl_w=False)  # discard via terminate (no save prompt)
