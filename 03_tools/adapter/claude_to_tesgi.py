#!/usr/bin/env python3
"""
Sync a Claude-style client workspace into canonical TESGI layout.

Claude source layout:
  clients/<client_id>/
    intake.md
    analysis/true.md
    analysis/north.md
    analysis/aligned.md
    memo.md
    sources/

TESGI target layout:
  02_client_work/<slug>/
    00_intake/intake.md
    00_intake/intake_ack.json
    01_sources/
    02_analysis/true.md
    02_analysis/north.md
    02_analysis/aligned.md
    03_memo/Decision_Memo.md
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def slugify_client_id(client_id: str) -> str:
    slug = re.sub(r"[^a-z0-9_-]+", "-", client_id.lower()).strip("-")
    slug = re.sub(r"-{2,}", "-", slug)
    if not slug:
        raise ValueError("client_id produced an empty slug")
    if not re.match(r"^[a-z0-9][a-z0-9_-]*$", slug):
        raise ValueError("Generated slug is invalid")
    return slug


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def copy_if_exists(src: Path, dst: Path) -> bool:
    if not src.is_file():
        return False
    ensure_dir(dst.parent)
    shutil.copy2(src, dst)
    return True


def copy_tree_if_exists(src_dir: Path, dst_dir: Path) -> int:
    if not src_dir.is_dir():
        return 0
    copied = 0
    ensure_dir(dst_dir)
    for src in src_dir.rglob("*"):
        if not src.is_file():
            continue
        rel = src.relative_to(src_dir)
        dst = dst_dir / rel
        ensure_dir(dst.parent)
        shutil.copy2(src, dst)
        copied += 1
    return copied


def write_intake_ack(path: Path, client_id: str, slug: str) -> None:
    payload = {
        "status": "ingested_from_claude",
        "source_client_id": client_id,
        "slug": slug,
    }
    ensure_dir(path.parent)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )


def ensure_tesgi_scaffold(base_dir: Path) -> None:
    for name in [
        "00_intake",
        "01_sources",
        "02_analysis",
        "03_memo",
        "04_package",
        "05_change_log",
    ]:
        ensure_dir(base_dir / name)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import a Claude client folder into canonical TESGI workspace"
    )
    parser.add_argument("client_id", help="Claude client directory name under clients/")
    parser.add_argument(
        "--claude-root",
        default=Path("..") / "TESGI_Claudvisor" / "clients",
        type=Path,
        help="Path to Claude clients root (default: ../TESGI_Claudvisor/clients)",
    )
    parser.add_argument(
        "--tesgi-root",
        default=Path("02_client_work"),
        type=Path,
        help="Path to TESGI canonical client root (default: 02_client_work)",
    )
    parser.add_argument(
        "--slug",
        help="Override generated TESGI slug (default: slugify(client_id))",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing target files if present",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = repo_root()

    claude_root = (root / args.claude_root).resolve()
    tesgi_root = (root / args.tesgi_root).resolve()
    client_id = args.client_id
    slug = args.slug or slugify_client_id(client_id)

    src = claude_root / client_id
    dst = tesgi_root / slug

    if not src.is_dir():
        raise FileNotFoundError(f"Claude client path not found: {src}")
    if dst.exists() and not args.force:
        raise RuntimeError(
            f"TESGI slug already exists: {dst}. Use --force to overwrite target files."
        )

    ensure_tesgi_scaffold(dst)

    copied = {
        "intake": copy_if_exists(src / "intake.md", dst / "00_intake" / "intake.md"),
        "true": copy_if_exists(src / "analysis" / "true.md", dst / "02_analysis" / "true.md"),
        "north": copy_if_exists(
            src / "analysis" / "north.md", dst / "02_analysis" / "north.md"
        ),
        "aligned": copy_if_exists(
            src / "analysis" / "aligned.md", dst / "02_analysis" / "aligned.md"
        ),
        "memo": copy_if_exists(src / "memo.md", dst / "03_memo" / "Decision_Memo.md"),
    }
    sources_count = copy_tree_if_exists(src / "sources", dst / "01_sources")
    write_intake_ack(dst / "00_intake" / "intake_ack.json", client_id=client_id, slug=slug)

    summary = {
        "source": src.as_posix(),
        "target": dst.as_posix(),
        "slug": slug,
        "copied": copied,
        "sources_files_copied": sources_count,
    }
    print(json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
