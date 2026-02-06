#!/usr/bin/env python3
"""
Export a canonical TESGI workspace into Claude-style client layout.

TESGI source layout:
  02_client_work/<slug>/
    00_intake/intake.md
    00_intake/intake_ack.json
    01_sources/
    02_analysis/true.md
    02_analysis/north.md
    02_analysis/aligned.md
    02_analysis/esg.md
    03_memo/Decision_Memo.md

Claude target layout:
  clients/<client_id>/
    intake.md
    analysis/true.md
    analysis/north.md
    analysis/aligned.md
    analysis/esg.md
    memo.md
    sources/
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


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


def resolve_client_id(slug: str, intake_ack_path: Path, explicit_client_id: str | None) -> str:
    if explicit_client_id:
        return explicit_client_id
    if intake_ack_path.is_file():
        try:
            payload = json.loads(intake_ack_path.read_text(encoding="utf-8"))
            source_client_id = payload.get("source_client_id")
            if isinstance(source_client_id, str) and source_client_id.strip():
                return source_client_id.strip()
        except json.JSONDecodeError:
            pass
    return slug


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export canonical TESGI workspace into Claude clients layout"
    )
    parser.add_argument("slug", help="TESGI slug directory name under 02_client_work/")
    parser.add_argument(
        "--tesgi-root",
        default=Path("02_client_work"),
        type=Path,
        help="Path to TESGI canonical client root (default: 02_client_work)",
    )
    parser.add_argument(
        "--claude-root",
        default=Path("..") / "TESGI_Claudvisor" / "clients",
        type=Path,
        help="Path to Claude clients root (default: ../TESGI_Claudvisor/clients)",
    )
    parser.add_argument(
        "--client-id",
        help="Override target Claude client id (default: source_client_id from intake_ack or slug)",
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

    tesgi_root = (root / args.tesgi_root).resolve()
    claude_root = (root / args.claude_root).resolve()
    slug = args.slug

    src = tesgi_root / slug
    if not src.is_dir():
        raise FileNotFoundError(f"TESGI slug path not found: {src}")

    intake_ack_path = src / "00_intake" / "intake_ack.json"
    client_id = resolve_client_id(slug, intake_ack_path, args.client_id)
    dst = claude_root / client_id

    if args.sync_delete and not args.force:
        raise RuntimeError("--sync-delete requires --force")
    if dst.exists() and not args.force:
        raise RuntimeError(
            f"Claude client path already exists: {dst}. Use --force to overwrite target files."
        )

    ensure_dir(dst / "analysis")
    ensure_dir(dst / "sources")

    copied = {}
    pruned = {}
    file_mappings = {
        "intake": (src / "00_intake" / "intake.md", dst / "intake.md"),
        "true": (src / "02_analysis" / "true.md", dst / "analysis" / "true.md"),
        "north": (src / "02_analysis" / "north.md", dst / "analysis" / "north.md"),
        "aligned": (src / "02_analysis" / "aligned.md", dst / "analysis" / "aligned.md"),
        "esg": (src / "02_analysis" / "esg.md", dst / "analysis" / "esg.md"),
        "memo": (src / "03_memo" / "Decision_Memo.md", dst / "memo.md"),
    }
    for key, (src_file, dst_file) in file_mappings.items():
        copied_flag, pruned_flag = sync_file(src_file, dst_file, sync_delete=args.sync_delete)
        copied[key] = copied_flag
        pruned[key] = pruned_flag

    sources_count, sources_pruned = sync_tree(
        src / "01_sources",
        dst / "sources",
        sync_delete=args.sync_delete,
    )

    summary = {
        "source": src.as_posix(),
        "target": dst.as_posix(),
        "slug": slug,
        "client_id": client_id,
        "copied": copied,
        "pruned": pruned,
        "sources_files_copied": sources_count,
        "sources_files_pruned": sources_pruned,
    }
    print(json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
