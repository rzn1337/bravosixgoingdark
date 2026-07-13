from __future__ import annotations

import argparse
import os
import platform
import sys

from . import __version__
from .apps import find_editor, find_filemanager
from .backends import BackendUnavailable, describe_backend
from .config import load_settings
from .platform_detect import detect
from .screen import get_screen_size
from .util.duration import parse_duration
from .util.logging import setup_logging


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="b6gd",
        description="Lightweight cross-platform human-activity simulator (personal use).",
    )
    p.add_argument("--version", action="version", version=f"b6gd {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    def add_common(sp):
        sp.add_argument("--duration", help="e.g. 30m, 1h, 90s (default 30m)")
        sp.add_argument(
            "--activities",
            help="features to RUN (comma list): write,browse,idle,switch,watch",
        )
        sp.add_argument(
            "--exclude", help="features to turn OFF (comma list), e.g. write,watch"
        )
        sp.add_argument(
            "-i",
            "--interactive",
            action="store_true",
            help="choose features interactively before the run starts",
        )
        sp.add_argument("--sandbox", help="workspace dir (default ~/B6GDWorkspace)")
        sp.add_argument("--config", help="path to a JSON settings file")
        sp.add_argument("--log-level", help="DEBUG/INFO/WARNING")
        sp.add_argument("--killswitch", help="pynput hotkey, e.g. '<ctrl>+<alt>+q'")
        sp.add_argument("--seed", type=int, help="RNG seed for reproducible runs")
        sp.add_argument(
            "--assume-focus",
            action="store_true",
            default=None,
            help="(default) type even when window focus can't be verified (e.g. Wayland)",
        )
        sp.add_argument(
            "--strict-focus",
            action="store_true",
            default=None,
            help="only type when the editor's focus is verified (disables Wayland typing)",
        )
        sp.add_argument(
            "--order",
            choices=["shuffle", "weighted"],
            help="activity order: shuffle = equal & random (default), weighted = by weight",
        )

    add_common(sub.add_parser("run", help="live session (moves the real cursor/keyboard)"))
    add_common(
        sub.add_parser("dry-run", help="plan & log actions without moving anything")
    )
    doc = sub.add_parser("doctor", help="print environment & setup diagnostics")
    doc.add_argument("--config")
    doc.add_argument("--sandbox")

    return p


def _apply_overrides(settings, args):
    if getattr(args, "duration", None):
        settings.duration_s = parse_duration(args.duration)
    if getattr(args, "activities", None):
        settings.activities = [a.strip() for a in args.activities.split(",") if a.strip()]
    if getattr(args, "sandbox", None):
        settings.sandbox_dir = os.path.abspath(os.path.expanduser(args.sandbox))
    if getattr(args, "log_level", None):
        settings.log_level = args.log_level.upper()
    if getattr(args, "killswitch", None):
        settings.killswitch = args.killswitch
    if getattr(args, "seed", None) is not None:
        settings.seed = args.seed
    if getattr(args, "assume_focus", None):
        settings.assume_focus = True
    if getattr(args, "strict_focus", None):
        settings.assume_focus = False
    if getattr(args, "order", None):
        settings.schedule.order = args.order
    return settings


def resolve_activities(all_names, selected, exclude):
    """Final ordered activity list: start from ``selected`` (or all), keep only
    known names, then drop anything in ``exclude``."""
    base = [n for n in (selected or all_names) if n in all_names]
    ex = {e for e in (exclude or [])}
    return [n for n in base if n not in ex]


def _parse_feature_selection(resp, all_names, preselected):
    """Interpret the interactive prompt response. Empty keeps ``preselected``;
    otherwise the typed names ARE the selection (canonical order, unknown names
    ignored)."""
    resp = (resp or "").strip()
    if not resp:
        return list(preselected)
    chosen = {t for t in (tok.strip().lower() for tok in resp.replace(",", " ").split()) if t in all_names}
    return [n for n in all_names if n in chosen]


def _interactive_select(all_names, preselected):
    import sys

    if not sys.stdin or not sys.stdin.isatty():
        return preselected
    print("Available features:", ", ".join(all_names))
    print("Selected now    :", ", ".join(preselected) if preselected else "(none)")
    print("Type the features to RUN (space or comma separated), e.g. `browse idle`.")
    print("Press Enter alone to keep the current selection.")
    try:
        resp = input("> ").strip()
    except EOFError:
        return preselected
    final = _parse_feature_selection(resp, all_names, preselected)
    print("Running:", ", ".join(final) if final else "(nothing selected)")
    return final


def cmd_doctor(settings) -> int:
    info = detect()
    try:
        import pynput

        pynput_status = getattr(pynput, "__version__", "installed")
        pynput_ok = True
    except Exception as exc:  # pragma: no cover - env dependent
        pynput_status = f"NOT INSTALLED ({exc})"
        pynput_ok = False

    editor = find_editor(info, settings.editor_cmd) or "(none found)"
    fm = find_filemanager(info, settings.filemanager_cmd) or "(none found)"
    w, h = get_screen_size(info)

    lines = [
        "B6GD doctor",
        "=" * 40,
        f"version        : {__version__}",
        f"python         : {platform.python_version()}",
        f"OS             : {info.system}",
        f"platform       : {platform.platform()}",
        f"session type   : {info.session_type}",
        f"pynput         : {pynput_status}",
        f"backend (live) : {describe_backend(info)}",
        f"screen size    : {w}x{h}",
        f"editor         : {editor}",
        f"file manager   : {fm}",
        f"sandbox        : {settings.sandbox_dir}",
        f"kill-switch    : {settings.killswitch}",
    ]

    if info.is_wayland:
        import shutil

        if shutil.which("ydotool"):
            lines.append(
                "wayland        : ydotool found — live input should work "
                "(make sure ydotoold is running)"
            )
        else:
            lines.append(
                "wayland        : ydotool NOT found — live input unavailable. "
                "Install ydotool or use an Xorg session (see README)."
            )
    if info.is_linux and editor == "(none found)":
        lines.append("note           : no text editor found — e.g. `sudo apt install gedit`")

    print("\n".join(lines))

    ready = pynput_ok or info.is_wayland
    invoke = (
        os.path.basename(sys.executable)
        if getattr(sys, "frozen", False)
        else "python run.py"
    )
    if ready:
        print(f"\nReady. Try:  {invoke} dry-run --duration 20s")
    else:
        print("\nInstall the one dependency first:  pip install pynput")
    return 0 if ready else 1


def _run_session(settings, dry_run: bool) -> int:
    from .engine.session import Session

    try:
        session = Session(settings, dry_run=dry_run)
    except BackendUnavailable as exc:
        print(str(exc), file=sys.stderr)
        return 2
    try:
        return session.run()
    except KeyboardInterrupt:
        return 0


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    settings = load_settings(getattr(args, "config", None))
    _apply_overrides(settings, args)
    setup_logging(settings.log_level, settings.logfile or None)

    if args.command == "doctor":
        return cmd_doctor(settings)

    from .activities import REGISTRY

    all_names = list(REGISTRY)
    exclude = (
        [a.strip() for a in args.exclude.split(",") if a.strip()]
        if getattr(args, "exclude", None)
        else []
    )
    settings.activities = resolve_activities(all_names, settings.activities, exclude)
    if getattr(args, "interactive", False):
        settings.activities = _interactive_select(all_names, settings.activities)

    if args.command == "dry-run":
        return _run_session(settings, dry_run=True)
    if args.command == "run":
        return _run_session(settings, dry_run=False)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
