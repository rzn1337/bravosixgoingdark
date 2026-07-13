# B6GD

A lightweight, cross-platform simulator of natural human desktop activity —
curved cursor movement, realistic typing, opening a notes app and writing into
it, and browsing folders. Runs on **Windows** and **Ubuntu** (and, best-effort,
macOS).

> **Personal use only.** This is a private tool, not for distribution.

## Download & run (no setup)

You don't need Python or any code setup — grab the prebuilt executable from the
repo's **[Releases](../../releases)** page:

1. Download the file for your OS:
   - **Windows:** `b6gd-windows.exe`
   - **Ubuntu / Linux:** `b6gd-linux`
2. Run it from a terminal.

**Windows (PowerShell):**
```powershell
.\b6gd-windows.exe doctor
.\b6gd-windows.exe dry-run --duration 20s
.\b6gd-windows.exe run --duration 10m
```

**Ubuntu:**
```bash
chmod +x b6gd-linux
./b6gd-linux doctor
./b6gd-linux dry-run --duration 20s
./b6gd-linux run --duration 10m
```

Notes:
- **Windows SmartScreen** may warn about an unrecognized app — the exe is
  unsigned. Click **More info → Run anyway**.
- If the repo is **private**, you must be signed in to GitHub to download the
  release assets.
- Run it from a terminal (not a double-click) so you can read the log and stop
  with `Ctrl+C`. And remember the kill-switch: **`Ctrl`+`Alt`+`Q`**.

The executables are built automatically by GitHub Actions whenever a version tag
(`v*`) is pushed — see [`.github/workflows/release.yml`](.github/workflows/release.yml).

## Run configurations (choose which features run)

B6GD has five features. Enable or disable any of them per run.

| Feature  | What it does                                                        |
|----------|---------------------------------------------------------------------|
| `write`  | Opens a **blank** note editor and types a note (**never saved**).   |
| `browse` | Opens the file manager and navigates around the sandbox folder.     |
| `idle`   | Drifts the cursor and scrolls, like reading or thinking.            |
| `switch` | Alt-Tabs between open windows.                                      |
| `watch`  | Opens the browser to a YouTube search (GoHighLevel / CRM / n8n) and watches. |

There are three ways to choose what runs. They work with both `run` and
`dry-run`. Examples use the Linux binary; on Windows use `.\b6gd-windows.exe`
with the same flags.

**1. Everything (default) — just don't pass a feature flag:**
```bash
./b6gd-linux run --duration 10m
```

**2. Only specific features — `--activities` (comma list):**
```bash
./b6gd-linux run --activities write                 # only type notes
./b6gd-linux run --activities watch                 # only watch YouTube
./b6gd-linux run --activities write,watch           # type + watch
./b6gd-linux run --activities browse,idle,switch    # move around only
```

**3. Everything EXCEPT some features — `--exclude` (comma list):**
```bash
./b6gd-linux run --exclude watch                    # everything but the browser
./b6gd-linux run --exclude write,browse             # no typing, no file manager
```

**4. Pick interactively before it starts — `-i` / `--interactive`:**
```bash
./b6gd-linux run -i
# It lists the features; type the ones you want to RUN, then press Enter:
#   Available features: write, browse, idle, switch, watch
#   > browse idle          <- runs ONLY browse and idle
#   (press Enter alone to keep the current selection)
```

Notes:
- Unknown names are ignored, and `--exclude` is applied after `--activities`
  (so exclude wins).
- Point `watch` at **specific videos** with a config file:
  `--config my.json` where `my.json` is
  `{ "watch": { "urls": ["https://www.youtube.com/watch?v=VIDEO_ID"] } }`.
- On Wayland, `write` types by default; add `--strict-focus` to type only when
  the editor's focus can be verified.

## Command reference

Same three verbs everywhere: **`doctor`** (check setup) → **`dry-run`** (safe
preview, nothing moves) → **`run`** (live). Add `--help` to any command to see
every option.

**Windows** (PowerShell, in the folder you downloaded the exe to):
```powershell
Unblock-File .\b6gd-windows.exe        # clear the "downloaded from internet" flag
.\b6gd-windows.exe doctor
.\b6gd-windows.exe dry-run --duration 30s
.\b6gd-windows.exe run --duration 2m
```

**Linux — X11 / Xorg** (full features, no daemon needed):
```bash
chmod +x b6gd-linux
./b6gd-linux doctor                    # expect: session type: x11
./b6gd-linux dry-run --duration 30s
./b6gd-linux run --duration 2m
```

**Linux — Wayland** (needs ydotool; hotkey/auto-pause are unavailable here):
```bash
sudo systemctl enable --now ydotool    # start the input daemon
./b6gd-linux doctor                    # expect: backend (live): ydotool
./b6gd-linux run --duration 2m --assume-focus
```

**Stop a run:** `Ctrl+Alt+Q` (Windows / X11), slam the mouse to the top-left
corner, `Ctrl+C`, or from any terminal: `touch ~/.b6gd_stop`.

**Common flags:** `--duration 30m|1h|90s` · `--activities write,browse,idle,switch,watch`
· `--exclude write,watch` (turn features off) · `-i` (choose features interactively)
· `--sandbox <dir>` · `--seed 42` · `--config file.json` · `--log-level DEBUG`
· `--strict-focus` (require verified focus before typing).

**Where output goes:** generated notes land in `~/B6GDWorkspace/Notes/`
(`%USERPROFILE%\B6GDWorkspace\Notes\` on Windows).

## Design goals

- **Lightweight.** Exactly one third-party dependency (`pynput`); everything
  else is the Python standard library. No screenshots, no vision, no GUI
  framework. Near-zero idle CPU (event-driven waits).
- **Believable.** Motion follows curved Bézier paths with easing, tremor, and
  occasional overshoot; typing has per-keystroke jitter, thinking pauses, and
  realistic adjacent-key typos that get backspaced and fixed.
- **Safe by construction** (see below).

## Safety

This tool takes over your mouse and keyboard, so stopping it must be instant and
it must never touch your real files:

- **Kill-switch:** press **`Ctrl`+`Alt`+`Q`** anytime to hard-stop. You can also
  **slam the mouse into the top-left corner**, or press **`Ctrl`+`C`** in the
  terminal.
- **Auto-pause on takeover:** the moment you move the real mouse or press a key,
  automation pauses; it resumes after a few seconds of no human input.
- **Sandboxed workspace:** it only ever opens, types into, and browses files
  inside `~/B6GDWorkspace/` (created and seeded automatically). It never
  navigates to or writes your real documents.
- **Focus guard:** before typing, it confirms the editor it launched is actually
  in the foreground; otherwise it skips typing.
- **Dry-run mode:** plan and log everything without moving anything.

## Requirements

- Python **3.9+**
- `pynput` (the only runtime dependency) — for live runs. `dry-run`, `doctor`,
  and the tests need no third-party packages.

## Install

```bash
# From the project folder:
python -m pip install -r requirements.txt      # installs pynput
# ...or install as a command:
python -m pip install -e .                      # gives you the `b6gd` command
```

You can always run straight from source without installing:

```bash
python run.py doctor
```

### Ubuntu (X11 / Xorg) — recommended, no extra setup
Works out of the box with `pynput`. If you're unsure which session you're on,
run `python run.py doctor` (look at `session type`). To force X11, pick
**"Ubuntu on Xorg"** from the gear menu at the login screen.

### Ubuntu (Wayland) — needs ydotool
Wayland blocks normal synthetic input for security. Install `ydotool` (which
injects at the kernel `uinput` level) and run its daemon:

```bash
sudo apt install ydotool
sudo systemctl enable --now ydotool     # or run manually: sudo ydotoold &
```

If you get permission errors on `/dev/uinput`, add a udev rule and reload:

```bash
echo 'KERNEL=="uinput", MODE="0660", GROUP="input", OPTIONS+="static_node=uinput"' \
  | sudo tee /etc/udev/rules.d/80-uinput.rules
sudo udevadm control --reload-rules && sudo udevadm trigger
sudo usermod -aG input "$USER"          # then log out/in
```

The Wayland path is experimental, with two limitations: the global hotkey and
auto-pause can't arm (pynput needs X), so stop with **`Ctrl`+`C`** or, from
another terminal, **`touch ~/.b6gd_stop`**; and window focus can't be verified,
so the `write` activity types only if you pass **`--assume-focus`**. For the full
experience (hotkey kill-switch, auto-pause, no ydotool needed), use an **Xorg**
session.

### macOS (best-effort)
Grant your terminal **Accessibility** permission (System Settings → Privacy &
Security → Accessibility). Not a primary target.

## Quick start

```bash
python run.py doctor                       # check environment & setup
python run.py dry-run --duration 20s       # safe: logs actions, moves nothing
python run.py run --duration 10m           # live run for 10 minutes
```

## Commands & options

| Command    | What it does                                              |
|------------|----------------------------------------------------------|
| `doctor`   | Prints OS, session type, chosen backend, editor/file-manager found, screen size, sandbox path, kill-switch. |
| `dry-run`  | Full behavior loop with a no-op backend — nothing is moved, typed, or launched. |
| `run`      | Live session that drives the real cursor and keyboard.   |

Common options (for `run` / `dry-run`):

| Option          | Example                     | Meaning                              |
|-----------------|-----------------------------|--------------------------------------|
| `--duration`    | `30m`, `1h`, `90s`          | How long to run (default `30m`).     |
| `--activities`  | `write,browse,idle,switch`  | Which activities to enable.          |
| `--sandbox`     | `~/work-sim`                | Workspace directory.                 |
| `--config`      | `config/default.json`       | Load settings from JSON.             |
| `--killswitch`  | `<ctrl>+<alt>+k`            | Change the stop hotkey.              |
| `--seed`        | `42`                        | Reproducible randomness.             |
| `--log-level`   | `DEBUG`                     | Verbosity.                           |

## How it works

```
CLI ─▶ Session ─▶ Scheduler ─▶ Activity ─▶ Executor ─▶ InputBackend ─▶ OS
                                   │            │
                                   │            └─ humanize/ (bezier paths, keystroke timing)
                                   └─ content/ (offline Markov note generator)
        safety/ (kill-switch, takeover, sandbox, focus) wraps the whole run
```

- **Input backend** (`backends/`): atomic primitives (`move`, `click`, `type`,
  …). `pynput` on Windows/X11/macOS; `ydotool` on Wayland; a `dryrun` backend
  that executes nothing.
- **Humanization** (`humanize/`): pure functions that turn intent into
  waypoints and keystroke timings. Unit-tested, no display required.
- **Activities** (`activities/`): `write` (types a note, never saved), `browse`,
  `idle`, `switch`, `watch` (opens YouTube on GoHighLevel / CRM / n8n topics).
  Pick which run with `--activities` / `--exclude` / `-i`.
- **Engine** (`engine/`): the `Executor` drives primitives through the
  humanizer and the `Control` (pause/stop) object; the `Scheduler` picks the
  next activity; the `Session` runs the loop.
- **Content** (`content/`): a tiny word-level Markov chain over a bundled corpus
  produces varied, plausible notes — fully offline.

## Configuration

Copy `config/default.json`, edit, and pass with `--config`. Any subset of keys
is allowed; unspecified keys keep their defaults. Highlights:

- `mouse.curvature`, `mouse.tremor_px`, `mouse.overshoot_chance` — path realism.
- `typing.wpm`, `typing.typo_rate`, `typing.think_pause_*` — typing feel.
- `activity_weights` — relative frequency of each activity.
- `schedule.break_chance`, `schedule.break_*_s` — pacing / breaks.
- `takeover_cooldown_s` — how long to stay paused after you touch the input.

## Troubleshooting

- **Kill-switch didn't arm / "pynput import failed":** install pynput
  (`pip install pynput`). On Linux you may also need `python3-xlib`.
- **Nothing happens on Ubuntu:** you're probably on Wayland — see the ydotool
  section, or switch to an Xorg session. `doctor` tells you which.
- **Typing gets skipped in `run`:** the editor window wasn't detected in front;
  install a supported editor (`gedit`, etc.) or set `editor_cmd` in config.
- **It fought me for the mouse:** during a single ~1s motion burst it ignores
  input to avoid false triggers; use the kill-switch for an instant stop.

## Development

```bash
python -m pip install pytest
python -m pytest            # pure-function tests; no display needed
```

### Build your own executable

```bash
python -m pip install pynput pyinstaller
pyinstaller b6gd.spec   # produces dist/b6gd(.exe)
```

Note: PyInstaller can't cross-compile — build the Windows `.exe` on Windows and
the Linux binary on Linux. The GitHub Actions workflow does both for you on a
tag push.

## Project layout

```
src/b6gd/
  cli.py  config.py  platform_detect.py  screen.py  apps.py
  backends/   humanize/   activities/   content/   engine/   safety/   util/
assets/corpus/     # offline text for note generation
config/default.json
tests/
run.py             # zero-install launcher
```
