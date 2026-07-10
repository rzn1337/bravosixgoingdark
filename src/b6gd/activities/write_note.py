from __future__ import annotations

from .base import Activity


class WriteNote(Activity):
    """Open the notes editor on a blank document and type a generated note with
    human rhythm. It never saves — the note is discarded when the editor closes
    at the end of the session."""

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
        ctx.focus.activate(hints)  # best-effort: bring the editor to the front
        if not ctx.exe.wait(rng.uniform(0.3, 0.8)):
            return

        assume = getattr(ctx.settings, "assume_focus", True)
        if ctx.focus.can_detect():
            if not ctx.focus.wait_for(hints, timeout=6.0):
                if not assume:
                    ctx.log.warning("write: editor not in foreground — skipping typing.")
                    return
                ctx.log.warning(
                    "write: editor not confirmed in front; typing anyway (assume_focus)."
                )
        elif not assume:
            ctx.log.warning(
                "write: can't verify window focus (e.g. Wayland) and --strict-focus is "
                "set — skipping typing."
            )
            return
        else:
            ctx.log.info(
                "write: focus not verifiable here (e.g. Wayland) — typing into the "
                "editor just launched."
            )

        text = ctx.content.make_note()
        ctx.log.info("write: typing note (%d chars); not saving", len(text))
        ctx.exe.type_text(text)
        ctx.exe.wait(rng.uniform(1.0, 3.0))
