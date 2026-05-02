#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from pathlib import Path

from core.catalog_signature import sign_catalog, SIG_PATH

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "commands_catalog.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Sign commands_catalog.json with HMAC-SHA256")
    parser.add_argument("--secret", default=os.environ.get("AUTOHACK_CATALOG_SECRET", ""))
    parser.add_argument("--catalog", type=Path, default=CATALOG)
    parser.add_argument("--out", type=Path, default=SIG_PATH)
    args = parser.parse_args()

    if not args.secret:
        raise SystemExit("Missing secret. Use --secret or AUTOHACK_CATALOG_SECRET.")

    sig = sign_catalog(args.catalog, args.secret)
    args.out.write_text(sig + "\n", encoding="utf-8")
    print(f"Wrote signature to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
