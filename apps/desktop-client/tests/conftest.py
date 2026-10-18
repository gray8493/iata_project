"""AITA Desktop Client - pytest bootstrap.

Adds `apps/desktop-client/src` to sys.path so tests can import the
`core...`, `services...`, `database...` modules (import root per AGENTS.md).
"""
import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
