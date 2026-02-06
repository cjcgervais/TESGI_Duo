#!/usr/bin/env python3
"""Inspect orchestration status for a TESGI client workspace."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tesgi.orchestration.engine import OrchestrationEngine


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inspect current orchestration stage for a TESGI client slug"
    )
    parser.add_argument("slug", help="Client slug under 02_client_work/")
    parser.add_argument(
        "--tesgi-root",
        default=Path("02_client_work"),
        type=Path,
        help="Path to TESGI canonical client root (default: 02_client_work)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = repo_root()
    base_dir = (root / args.tesgi_root / args.slug).resolve()
    if not base_dir.is_dir():
        raise FileNotFoundError(f"Client slug path not found: {base_dir}")
    engine = OrchestrationEngine(base_dir)
    status = engine.evaluate()
    payload = {
        "slug": args.slug,
        "base_dir": base_dir.as_posix(),
        "status": status.as_dict(),
    }
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
