#!/usr/bin/env python3
"""
Sync a Claude-style client workspace into canonical TESGI layout.

Claude source layout:
  clients/<client_id>/
    intake.md
    analysis/true.md
    analysis/north.md
    analysis/aligned.md
    analysis/esg.md
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
    02_analysis/esg.md
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


def sync_file(src: Path, dst: Path, sync_delete: bool = False) -> tuple[bool, bool]:
    copied = False
    pruned = False
    if src.is_file():
        ensure_dir(dst.parent)
        shutil.copy2(src, dst)
        copied = True
    elif sync_delete and dst.is_file():
        dst.unlink()
        pruned = True
    return copied, pruned


def sync_tree(src_dir: Path, dst_dir: Path, sync_delete: bool = False) -> tuple[int, int]:
    copied = 0
    pruned = 0
    source_files: set[Path] = set()
    if src_dir.is_dir():
        ensure_dir(dst_dir)
        for src in src_dir.rglob("*"):
            if not src.is_file():
                continue
            rel = src.relative_to(src_dir)
            source_files.add(rel)
            dst = dst_dir / rel
            ensure_dir(dst.parent)
            shutil.copy2(src, dst)
            copied += 1
    if sync_delete and dst_dir.is_dir():
        for dst in sorted(dst_dir.rglob("*"), reverse=True):
            if dst.is_file():
                rel = dst.relative_to(dst_dir)
                if rel not in source_files:
                    dst.unlink()
                    pruned += 1
            elif dst.is_dir() and not any(dst.iterdir()):
                dst.rmdir()
    return copied, pruned


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
    parser.add_argument(
        "--sync-delete",
        action="store_true",
        help="With --force, prune stale files from mapped target paths",
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
    if args.sync_delete and not args.force:
        raise RuntimeError("--sync-delete requires --force")
    if dst.exists() and not args.force:
        raise RuntimeError(
            f"TESGI slug already exists: {dst}. Use --force to overwrite target files."
        )

    ensure_tesgi_scaffold(dst)

    copied = {}
    pruned = {}
    file_mappings = {
        "intake": (src / "intake.md", dst / "00_intake" / "intake.md"),
        "true": (src / "analysis" / "true.md", dst / "02_analysis" / "true.md"),
        "north": (src / "analysis" / "north.md", dst / "02_analysis" / "north.md"),
        "aligned": (src / "analysis" / "aligned.md", dst / "02_analysis" / "aligned.md"),
        "esg": (src / "analysis" / "esg.md", dst / "02_analysis" / "esg.md"),
        "memo": (src / "memo.md", dst / "03_memo" / "Decision_Memo.md"),
    }
    for key, (src_file, dst_file) in file_mappings.items():
        copied_flag, pruned_flag = sync_file(src_file, dst_file, sync_delete=args.sync_delete)
        copied[key] = copied_flag
        pruned[key] = pruned_flag

    sources_count, sources_pruned = sync_tree(
        src / "sources",
        dst / "01_sources",
        sync_delete=args.sync_delete,
    )
    write_intake_ack(dst / "00_intake" / "intake_ack.json", client_id=client_id, slug=slug)

    summary = {
        "source": src.as_posix(),
        "target": dst.as_posix(),
        "slug": slug,
        "copied": copied,
        "pruned": pruned,
        "sources_files_copied": sources_count,
        "sources_files_pruned": sources_pruned,
    }
    print(json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
