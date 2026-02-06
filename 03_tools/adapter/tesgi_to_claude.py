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
    03_memo/Decision_Memo.md

Claude target layout:
  clients/<client_id>/
    intake.md
    analysis/true.md
    analysis/north.md
    analysis/aligned.md
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

    if dst.exists() and not args.force:
        raise RuntimeError(
            f"Claude client path already exists: {dst}. Use --force to overwrite target files."
        )

    ensure_dir(dst / "analysis")
    ensure_dir(dst / "sources")

    copied = {
        "intake": copy_if_exists(src / "00_intake" / "intake.md", dst / "intake.md"),
        "true": copy_if_exists(src / "02_analysis" / "true.md", dst / "analysis" / "true.md"),
        "north": copy_if_exists(
            src / "02_analysis" / "north.md", dst / "analysis" / "north.md"
        ),
        "aligned": copy_if_exists(
            src / "02_analysis" / "aligned.md", dst / "analysis" / "aligned.md"
        ),
        "memo": copy_if_exists(src / "03_memo" / "Decision_Memo.md", dst / "memo.md"),
    }
    sources_count = copy_tree_if_exists(src / "01_sources", dst / "sources")

    summary = {
        "source": src.as_posix(),
        "target": dst.as_posix(),
        "slug": slug,
        "client_id": client_id,
        "copied": copied,
        "sources_files_copied": sources_count,
    }
    print(json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
