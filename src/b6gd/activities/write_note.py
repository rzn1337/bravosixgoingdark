from __future__ import annotations

from .base import Activity


class WriteNote(Activity):
    """Open the notes editor on a fresh sandbox file, type a generated note
    with human rhythm, and usually save. Types only after confirming the
    editor is actually in the foreground."""

    name = "write"

    def run(self) -> None:
        ctx = self.ctx
        rng = ctx.rng

        path = ctx.sandbox.new_note_path()
        ctx.log.info("write: opening editor (%s) on %s", ctx.apps.editor or "default", path)
        proc = ctx.apps.launch_editor(path)
        if proc is not None:
            ctx.tracked.append(proc)

        if not ctx.exe.wait(rng.uniform(1.5, 3.0)):  # let the app come up
            return

        hints = ctx.apps.editor_title_hints(path)
        if ctx.focus.can_detect():
            if not ctx.focus.wait_for(hints, timeout=6.0):
                ctx.log.warning(
                    "write: editor not detected in foreground — skipping typing "
                    "(focus guard prevents stray keystrokes)."
                )
                return
        elif not getattr(ctx.settings, "assume_focus", False):
            ctx.log.warning(
                "write: can't verify window focus on this session (e.g. Wayland) — "
                "skipping typing to avoid stray keystrokes. Re-run with --assume-focus "
                "to type into the just-launched editor anyway."
            )
            return
        else:
            ctx.log.warning(
                "write: focus unverifiable — typing into the just-launched editor "
                "(--assume-focus)."
            )

        text = ctx.content.make_note()
        ctx.log.info("write: typing note (%d chars)", len(text))
        if not ctx.exe.type_text(text):
            return

        if rng.random() < 0.75:
            ctx.log.info("write: saving (Ctrl+S)")
            if not ctx.exe.hotkey("ctrl", "s"):
                return
            ctx.exe.wait(rng.uniform(0.6, 1.4))

        ctx.exe.wait(rng.uniform(1.0, 3.0))
