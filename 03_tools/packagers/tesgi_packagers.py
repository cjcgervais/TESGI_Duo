"""Packaging helpers for TESGI CLI and scripts."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from tesgi import __version__

MANIFEST_REQUIRED_FILES = (
    "00_intake/intake.md",
    "00_intake/intake_ack.json",
    "02_analysis/true.md",
    "02_analysis/north.md",
    "02_analysis/aligned.md",
    "03_memo/Decision_Memo.md",
    "03_memo/memo.md",
    "04_package/memo.pdf",
    "04_package/invoice.pdf",
    "04_package/receipt.pdf",
    "04_package/manifest.json",
    "04_package/gate_report.json",
    "04_package/runlog.jsonl",
)

MANIFEST_OPTIONAL_FILES = (
    "01_sources/sources_manifest.json",
    "02_analysis/esg.md",
)

PACKAGE_SCHEMA_VERSION = "1.0"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def python_version() -> str:
    info = sys.version_info
    return f"{info.major}.{info.minor}.{info.micro}"


def file_sha256(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )


def list_manifest_files(base_dir: Path) -> list[str]:
    files = []
    for rel in MANIFEST_REQUIRED_FILES:
        if (base_dir / rel).is_file():
            files.append(rel)
    for rel in MANIFEST_OPTIONAL_FILES:
        if (base_dir / rel).is_file() and rel not in files:
            files.append(rel)
    return files


def compute_manifest(base_dir: Path, command_name: str = "package") -> dict:
    root = Path(__file__).resolve().parents[2]
    try:
        base_value = base_dir.relative_to(root).as_posix()
    except ValueError:
        base_value = base_dir.as_posix()

    entries = []
    for rel in list_manifest_files(base_dir):
        path = base_dir / rel
        stat = path.stat()
        entries.append(
            {
                "path": rel,
                "sha256": file_sha256(path),
                "size": stat.st_size,
                "mtime": int(stat.st_mtime),
            }
        )

    return {
        "generated_at": utc_now(),
        "base_dir": base_value,
        "tesgi_version": __version__,
        "python_version": python_version(),
        "tooling": {
            "cli": "tesgi",
            "command": command_name,
            "package_schema_version": PACKAGE_SCHEMA_VERSION,
        },
        "files": entries,
    }


def write_manifest(base_dir: Path, command_name: str = "package") -> dict:
    manifest_path = base_dir / "04_package" / "manifest.json"
    manifest = compute_manifest(base_dir, command_name=command_name)
    write_json(manifest_path, manifest)
    # Recompute so manifest.json hashes include its own final bytes.
    manifest = compute_manifest(base_dir, command_name=command_name)
    write_json(manifest_path, manifest)
    return manifest


def _sanitize_pdf_text(text: str) -> str:
    value = text.replace("\\", "\\\\")
    value = value.replace("(", "\\(").replace(")", "\\)")
    return "".join(ch if 32 <= ord(ch) <= 126 else "?" for ch in value)


def _build_pdf_bytes(lines: Iterable[str]) -> bytes:
    content_lines = [
        "BT",
        "/F1 11 Tf",
        "72 760 Td",
    ]
    first = True
    for raw in lines:
        text = _sanitize_pdf_text(raw.strip())
        if not text:
            text = " "
        if first:
            content_lines.append(f"({text}) Tj")
            first = False
        else:
            content_lines.append(f"0 -14 Td ({text}) Tj")
    if first:
        content_lines.append("( ) Tj")
    content_lines.append("ET")
    stream = "\n".join(content_lines).encode("latin-1", errors="replace")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Count 1 /Kids [3 0 R] >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>",
        f"<< /Length {len(stream)} >>\nstream\n".encode("ascii") + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for idx, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{idx} 0 obj\n".encode("ascii"))
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")

    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode(
            "ascii"
        )
    )
    return bytes(pdf)


def write_simple_pdf(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(_build_pdf_bytes(lines))


def ensure_memo_alias(base_dir: Path) -> Path:
    src = base_dir / "03_memo" / "Decision_Memo.md"
    if not src.is_file():
        raise RuntimeError("03_memo/Decision_Memo.md is required")
    dst = base_dir / "03_memo" / "memo.md"
    dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    return dst


def build_memo_artifacts(base_dir: Path, slug: str) -> dict[str, str]:
    memo_alias = ensure_memo_alias(base_dir)
    memo_pdf = base_dir / "04_package" / "memo.pdf"
    lines = [f"TESGI Decision Memo - {slug}"]
    for line in memo_alias.read_text(encoding="utf-8").splitlines():
        if line.strip():
            lines.append(line.strip())
        if len(lines) >= 55:
            break
    write_simple_pdf(memo_pdf, lines)
    return {
        "memo_markdown": memo_alias.as_posix(),
        "memo_pdf": memo_pdf.as_posix(),
    }


def ensure_package_documents(base_dir: Path, slug: str) -> dict[str, str]:
    invoice_pdf = base_dir / "04_package" / "invoice.pdf"
    receipt_pdf = base_dir / "04_package" / "receipt.pdf"

    write_simple_pdf(
        invoice_pdf,
        [
            f"TESGI Advisory Invoice - {slug}",
            "This is a generated packaging placeholder invoice.",
            "For governance testing and integrity verification only.",
        ],
    )
    write_simple_pdf(
        receipt_pdf,
        [
            f"TESGI Advisory Receipt - {slug}",
            "This is a generated packaging placeholder receipt.",
            "For governance testing and integrity verification only.",
        ],
    )

    return {
        "invoice_pdf": invoice_pdf.as_posix(),
        "receipt_pdf": receipt_pdf.as_posix(),
    }


def ensure_runlog_file(base_dir: Path) -> Path:
    runlog = base_dir / "04_package" / "runlog.jsonl"
    runlog.parent.mkdir(parents=True, exist_ok=True)
    if not runlog.exists():
        runlog.write_text("", encoding="utf-8")
    return runlog


def append_runlog_event(base_dir: Path, payload: dict) -> Path:
    runlog = ensure_runlog_file(base_dir)
    with runlog.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True, ensure_ascii=True) + "\n")
    return runlog


def prepare_package_artifacts(base_dir: Path, slug: str) -> dict[str, str]:
    artifacts = {}
    artifacts.update(build_memo_artifacts(base_dir, slug))
    artifacts.update(ensure_package_documents(base_dir, slug))
    runlog = ensure_runlog_file(base_dir)
    artifacts["runlog"] = runlog.as_posix()
    return artifacts


def write_gate_report(base_dir: Path, slug: str, results: Iterable) -> dict:
    result_list = list(results)
    report = {
        "slug": slug,
        "generated_at": utc_now(),
        "status": "pass" if all(getattr(r, "status", False) for r in result_list) else "fail",
        "gates": [r.as_dict() for r in result_list],
    }
    path = base_dir / "04_package" / "gate_report.json"
    write_json(path, report)
    return report


def initialize_package_skeleton(base_dir: Path, slug: str) -> None:
    prepare_package_artifacts(base_dir, slug)
    gate_report_path = base_dir / "04_package" / "gate_report.json"
    if not gate_report_path.is_file():
        write_json(
            gate_report_path,
            {
                "slug": slug,
                "generated_at": utc_now(),
                "status": "pending",
                "gates": [],
            },
        )
    write_manifest(base_dir, command_name="init-client")
