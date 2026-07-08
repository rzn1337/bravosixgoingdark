"""Packaging entry point (used by PyInstaller).

Unlike run.py, this assumes the ``humansim`` package is importable — the spec
adds ``src`` to PyInstaller's path so the frozen build resolves it statically.
"""
import sys

from humansim.cli import main

if __name__ == "__main__":
    sys.exit(main())
