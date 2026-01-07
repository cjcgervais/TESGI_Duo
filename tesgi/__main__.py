import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDE_FILES = {
    "04_package/manifest.json",
    "04_package/gate_report.json",
}


class GateResult:
    def __init__(self, gate_id, name, status, detail):
        self.gate_id = gate_id
        self.name = name
        self.status = status
        self.detail = detail

    def as_dict(self):
        return {
            "id": self.gate_id,
            "name": self.name,
            "status": "pass" if self.status else "fail",
            "detail": self.detail,
        }


def utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_simple_yaml(path):
    data = {}
    current_key = None
    if not path.is_file():
        return data
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if raw.lstrip().startswith("- "):
            if current_key and isinstance(data.get(current_key), list):
                value = raw.lstrip()[2:].strip()
                data[current_key].append(value)
            continue
        if ":" in raw:
            key, rest = raw.split(":", 1)
            key = key.strip()
            rest = rest.strip()
            if rest:
                data[key] = rest
                current_key = None
            else:
                data[key] = []
                current_key = key
    return data


def validate_slug(slug):
    if not re.match(r"^[a-z0-9][a-z0-9_-]*$", slug):
        raise ValueError("Slug must be lowercase alphanumeric with optional - or _")


def slug_path(slug):
    return ROOT / "02_client_work" / slug


def list_client_files(base_dir):
    files = []
    for path in base_dir.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(base_dir).as_posix()
        if rel in EXCLUDE_FILES:
            continue
        files.append(rel)
    return sorted(files)


def file_sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def compute_manifest(base_dir):
    try:
        base_value = base_dir.relative_to(ROOT).as_posix()
    except ValueError:
        base_value = base_dir.as_posix()
    entries = []
    for rel in list_client_files(base_dir):
        path = base_dir / rel
        entries.append(
            {
                "path": rel,
                "sha256": file_sha256(path),
                "mtime": int(path.stat().st_mtime),
            }
        )
    return {
        "generated_at": utc_now(),
        "base_dir": base_value,
        "files": entries,
    }


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )


def write_manifest(base_dir):
    manifest = compute_manifest(base_dir)
    manifest_path = base_dir / "04_package" / "manifest.json"
    write_json(manifest_path, manifest)
    return manifest


def find_memo_files(base_dir):
    memo_dir = base_dir / "03_memo"
    if not memo_dir.is_dir():
        return []
    memo_files = []
    for path in memo_dir.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() in {".md", ".txt"}:
            memo_files.append(path)
    return sorted(memo_files)


def has_sections(content, sections):
    missing = []
    for section in sections:
        found = False
        for line in content.splitlines():
            line_l = line.strip().lower()
            if not line_l.startswith("#"):
                continue
            if section.lower() in line_l:
                found = True
                break
        if not found:
            missing.append(section)
    return missing


def gate_kernel():
    kernel_path = ROOT / "00_governance" / "KERNEL.md"
    if not kernel_path.is_file():
        return GateResult("A", "Kernel completeness", False, "KERNEL.md missing")
    required = ["TRUE", "NORTH", "ALIGNED"]
    positions = {}
    for idx, line in enumerate(kernel_path.read_text(encoding="utf-8").splitlines()):
        line = line.strip()
        if line.startswith("## "):
            title = line[3:].strip().upper()
            if title in required and title not in positions:
                positions[title] = idx
    missing = [r for r in required if r not in positions]
    if missing:
        return GateResult(
            "A",
            "Kernel completeness",
            False,
            "Missing sections: " + ", ".join(missing),
        )
    if not (positions["TRUE"] < positions["NORTH"] < positions["ALIGNED"]):
        return GateResult(
            "A",
            "Kernel completeness",
            False,
            "Section order must be TRUE, NORTH, ALIGNED",
        )
    return GateResult("A", "Kernel completeness", True, "OK")


def gate_memo_sections(base_dir):
    required = ["Decision State", "What This Memo Does Not Say"]
    memo_files = find_memo_files(base_dir)
    if not memo_files:
        return GateResult("B", "Memo required sections", False, "No memo files found")
    missing_files = {}
    for memo in memo_files:
        content = memo.read_text(encoding="utf-8")
        missing = has_sections(content, required)
        if missing:
            missing_files[memo.name] = missing
    if missing_files:
        detail = "; ".join(
            f"{name} missing {', '.join(sections)}"
            for name, sections in sorted(missing_files.items())
        )
        return GateResult("B", "Memo required sections", False, detail)
    return GateResult("B", "Memo required sections", True, "OK")


def load_language_rules():
    rules_path = ROOT / "00_governance" / "LANGUAGE_RULES.yml"
    data = parse_simple_yaml(rules_path)
    forbidden = data.get("forbidden_terms", []) or []
    required = data.get("required_sections", []) or []
    return forbidden, required


def gate_language(base_dir):
    memo_files = find_memo_files(base_dir)
    if not memo_files:
        return GateResult("C", "Language lint", False, "No memo files found")
    forbidden, required = load_language_rules()
    violations = []
    missing_sections = {}
    for memo in memo_files:
        content = memo.read_text(encoding="utf-8")
        content_l = content.lower()
        bad_terms = [term for term in forbidden if term.lower() in content_l]
        if bad_terms:
            violations.append(f"{memo.name} contains {', '.join(sorted(set(bad_terms)))}")
        if required:
            missing = has_sections(content, required)
            if missing:
                missing_sections[memo.name] = missing
    if violations or missing_sections:
        details = []
        if violations:
            details.append("; ".join(violations))
        if missing_sections:
            details.append(
                "; ".join(
                    f"{name} missing {', '.join(sections)}"
                    for name, sections in sorted(missing_sections.items())
                )
            )
        return GateResult("C", "Language lint", False, " | ".join(details))
    return GateResult("C", "Language lint", True, "OK")


def gate_manifest(base_dir):
    manifest_path = base_dir / "04_package" / "manifest.json"
    if not manifest_path.is_file():
        return GateResult("D", "Packaging integrity", False, "manifest.json missing")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return GateResult("D", "Packaging integrity", False, f"manifest.json invalid: {exc}")
    files = manifest.get("files")
    if not isinstance(files, list):
        return GateResult("D", "Packaging integrity", False, "manifest.json files must be a list")
    manifest_map = {}
    for entry in files:
        if not isinstance(entry, dict):
            return GateResult("D", "Packaging integrity", False, "manifest entry must be object")
        path = entry.get("path")
        sha256 = entry.get("sha256")
        mtime = entry.get("mtime")
        if not path or not sha256 or mtime is None:
            return GateResult("D", "Packaging integrity", False, "manifest entry missing fields")
        manifest_map[path] = {"sha256": sha256, "mtime": int(mtime)}
    expected = compute_manifest(base_dir)["files"]
    expected_map = {entry["path"]: entry for entry in expected}
    if set(manifest_map.keys()) != set(expected_map.keys()):
        missing = sorted(set(expected_map.keys()) - set(manifest_map.keys()))
        extra = sorted(set(manifest_map.keys()) - set(expected_map.keys()))
        parts = []
        if missing:
            parts.append("missing: " + ", ".join(missing))
        if extra:
            parts.append("extra: " + ", ".join(extra))
        return GateResult("D", "Packaging integrity", False, " | ".join(parts))
    mismatches = []
    for path, expected_entry in expected_map.items():
        actual = manifest_map[path]
        if actual["sha256"] != expected_entry["sha256"]:
            mismatches.append(f"hash {path}")
        if actual["mtime"] != expected_entry["mtime"]:
            mismatches.append(f"mtime {path}")
    if mismatches:
        return GateResult("D", "Packaging integrity", False, "mismatch: " + ", ".join(mismatches))
    return GateResult("D", "Packaging integrity", True, "OK")


def run_gates(base_dir):
    return [
        gate_kernel(),
        gate_memo_sections(base_dir),
        gate_language(base_dir),
        gate_manifest(base_dir),
    ]


def print_results(results):
    for result in results:
        status = "PASS" if result.status else "FAIL"
        print(f"{result.gate_id} {status}: {result.name} - {result.detail}")


def write_gate_report(base_dir, slug, results):
    report = {
        "slug": slug,
        "generated_at": utc_now(),
        "status": "pass" if all(r.status for r in results) else "fail",
        "gates": [r.as_dict() for r in results],
    }
    path = base_dir / "04_package" / "gate_report.json"
    write_json(path, report)
    return report


def cmd_init_client(slug):
    validate_slug(slug)
    base_dir = slug_path(slug)
    if base_dir.exists():
        raise RuntimeError(f"Client slug already exists: {slug}")
    for name in [
        "00_intake",
        "01_sources",
        "02_analysis",
        "03_memo",
        "04_package",
        "05_change_log",
    ]:
        (base_dir / name).mkdir(parents=True, exist_ok=True)
    memo_path = base_dir / "03_memo" / "Decision_Memo.md"
    memo_path.write_text(
        "# Decision Memo\n\n"
        "## Decision State\n"
        "Draft. This memo reflects current analysis and may change with new evidence.\n\n"
        "## What This Memo Does Not Say\n"
        "- It does not commit to outcomes or timelines.\n"
        "- It does not provide licensed professional advice.\n",
        encoding="utf-8",
    )
    write_manifest(base_dir)
    print(f"Initialized client: {slug}")


def cmd_validate(slug, base_dir=None):
    if base_dir is None:
        validate_slug(slug)
        base_dir = slug_path(slug)
    if not base_dir.is_dir():
        raise RuntimeError(f"Client slug not found: {slug}")
    results = run_gates(base_dir)
    print_results(results)
    if all(r.status for r in results):
        print("VALIDATION: PASS")
        return 0, results
    print("VALIDATION: FAIL")
    return 1, results


def cmd_run(slug):
    validate_slug(slug)
    base_dir = slug_path(slug)
    if not base_dir.is_dir():
        raise RuntimeError(f"Client slug not found: {slug}")
    write_manifest(base_dir)
    exit_code, results = cmd_validate(slug, base_dir=base_dir)
    write_gate_report(base_dir, slug, results)
    record = {
        "slug": slug,
        "generated_at": utc_now(),
        "status": "pass" if exit_code == 0 else "fail",
        "manifest": (base_dir / "04_package" / "manifest.json").as_posix(),
        "gate_report": (base_dir / "04_package" / "gate_report.json").as_posix(),
    }
    record_path = ROOT / "runs" / f"{slug}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    write_json(record_path, record)
    if exit_code != 0:
        sys.exit(exit_code)


def cmd_eval():
    suite_path = ROOT / "04_evals" / "regression_suite.yml"
    data = parse_simple_yaml(suite_path)
    case_paths = data.get("cases") or []
    if not case_paths:
        raise RuntimeError("No cases defined in regression_suite.yml")
    failures = 0
    for case_path in case_paths:
        base_dir = ROOT / case_path
        slug = base_dir.name
        if not base_dir.is_dir():
            print(f"EVAL SKIP: {case_path} not found")
            failures += 1
            continue
        exit_code, _results = cmd_validate(slug, base_dir=base_dir)
        if exit_code != 0:
            failures += 1
    if failures:
        print(f"EVAL: FAIL ({failures} case(s))")
        sys.exit(1)
    print("EVAL: PASS")


def build_parser():
    parser = argparse.ArgumentParser(prog="tesgi", description="TESGI Advisory OS tooling")
    sub = parser.add_subparsers(dest="command", required=True)

    init_client = sub.add_parser("init-client", help="Initialize client workspace")
    init_client.add_argument("slug")

    validate = sub.add_parser("validate", help="Validate client workspace")
    validate.add_argument("slug")

    run = sub.add_parser("run", help="Run validation and package outputs")
    run.add_argument("slug")

    sub.add_parser("eval", help="Run evaluation suite")
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "init-client":
        cmd_init_client(args.slug)
        return
    if args.command == "validate":
        exit_code, _ = cmd_validate(args.slug)
        sys.exit(exit_code)
    if args.command == "run":
        cmd_run(args.slug)
        return
    if args.command == "eval":
        cmd_eval()
        return


if __name__ == "__main__":
    main()
