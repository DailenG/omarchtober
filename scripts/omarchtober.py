#!/usr/bin/env python3
"""Repository-local entry point for the Omarchtober renderer."""

from __future__ import annotations

import sys
from pathlib import Path

PLUGIN_DIR = Path(__file__).resolve().parent.parent
if str(PLUGIN_DIR) not in sys.path:
    sys.path.insert(0, str(PLUGIN_DIR))

from omarchtober.app import main


if __name__ == "__main__":
    raise SystemExit(main())
