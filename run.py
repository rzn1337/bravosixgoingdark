#!/usr/bin/env python3
"""Zero-install launcher.

Lets you run HumanSim straight from the source tree without `pip install`:

    python run.py doctor
    python run.py dry-run --duration 20s
    python run.py run --duration 10m

(You can also `pip install -e .` and use the `humansim` command instead.)
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from humansim.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
