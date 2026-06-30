#!/usr/bin/env python3
from __future__ import annotations

# ruff: noqa: E402

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.audit_chain import verify


def main() -> int:
    ok, line = verify()
    if ok:
        print(f"Execution chain valid ({line} events).")
        return 0
    print(f"Execution chain invalid at line {line}.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
