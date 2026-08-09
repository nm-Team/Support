#!/usr/bin/env python
# manage.py
"""Backward-compatible CLI wrapper (delegates to the nmteam package).

Kept so ``dev.sh`` / ``dev.ps1`` / ``dev.bat`` and muscle memory for
``python manage.py <command>`` keep working. Run it through uv:

    uv run python manage.py dev
"""

import sys

from nmteam_support.cli import main

if __name__ == "__main__":
    sys.exit(main())
