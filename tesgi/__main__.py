import argparse
import hashlib
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from . import __version__
from .orchestration import OrchestrationEngine, OrchestrationError

ROOT = Path(__file__).resolve().parents[1]
ALLOWLIST_FILES = (
    "00_intake/intake.md",
    "00_intake/intake_ack.json",
    "02_analysis/true.md",
    "02_analysis/north.md",
    "02_analysis/aligned.md",
    "03_memo/Decision_Memo.md",
    "04_package/manifest.json",
    "04_package/gate_report.json",
)


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
    for rel in ALLOWLIST_FILES:
        path = base_dir / rel
        if path.is_file():
            files.append(rel)
    return files


def file_sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def python_version():
    info = sys.version_info
    return f"{info.major}.{info.minor}.{info.micro}"


def compute_manifest(base_dir):
    try:
        base_value = base_dir.relative_to(ROOT).as_posix()
    except ValueError:
        base_value = base_dir.as_posix()
    entries = []
    for rel in list_client_files(base_dir):
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
        "files": entries,
    }


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )


def write_manifest(base_dir):
    manifest_path = base_dir / "04_package" / "manifest.json"
    manifest = compute_manifest(base_dir)
    write_json(manifest_path, manifest)
    manifest = compute_manifest(base_dir)
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


def normalize_text(text):
    normalized = text
    replacements = {
        "\u2019": "'",
        "\u2018": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
    }
    for old, new in replacements.items():
        normalized = normalized.replace(old, new)
    return normalized


def phrase_present(content, phrase):
    phrase = normalize_text(phrase).strip()
    if not phrase:
        return False
    tokens = phrase.split()
    pattern = r"\b" + r"\s+".join(re.escape(token) for token in tokens) + r"\b"
    haystack = normalize_text(content)
    return re.search(pattern, haystack, flags=re.IGNORECASE) is not None


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


def extract_section(content, section_name):
    lines = content.splitlines()
    section_pattern = re.compile(
        rf"^\s*#{{1,6}}\s+.*{re.escape(section_name)}.*$",
        flags=re.IGNORECASE,
    )
    start = None
    for idx, line in enumerate(lines):
        if section_pattern.match(line):
            start = idx + 1
            break
    if start is None:
        return ""
    end = len(lines)
    for idx in range(start, len(lines)):
        if re.match(r"^\s*#{1,6}\s+", lines[idx]):
            end = idx
            break
    return "\n".join(lines[start:end]).strip()


def parse_decision_states(content):
    section = extract_section(content, "Decision State")
    if not section:
        return []
    selected = []
    for raw_line in section.splitlines():
        line = normalize_text(raw_line).strip()
        line_l = line.lower()
        if not line_l:
            continue
        checked = ("[x]" in line_l) or ("\u2611" in line)
        if not checked:
            continue
        if "proceed" in line_l:
            selected.append("Proceed")
        if "pause" in line_l:
            selected.append("Pause")
        if "avoid" in line_l or "walk away" in line_l:
            selected.append("Avoid")
    unique = []
    for state in ["Proceed", "Pause", "Avoid"]:
        if state in selected:
            unique.append(state)
    if unique:
        return unique
    explicit = re.search(
        r"decision\s*state\s*:\s*(proceed|pause|avoid|walk\s*away)",
        normalize_text(content),
        flags=re.IGNORECASE,
    )
    if not explicit:
        return []
    value = explicit.group(1).lower().replace(" ", "")
    if value in {"avoid", "walkaway"}:
        return ["Avoid"]
    if value == "pause":
        return ["Pause"]
    return ["Proceed"]


def section_has_list_items(content, section_name):
    section = extract_section(content, section_name)
    if not section:
        return False
    for raw_line in section.splitlines():
        line = raw_line.strip()
        if re.match(r"^[-*]\s+\S+", line):
            return True
        if re.match(r"^\d+\.\s+\S+", line):
            return True
    return False


def section_has_content(content, section_name):
    section = extract_section(content, section_name)
    if not section:
        return False
    for raw_line in section.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if re.match(r"^[-*]\s*$", line):
            continue
        if re.match(r"^\d+\.\s*$", line):
            continue
        return True
    return False


def proceed_blockers(base_dir):
    blockers = []
    marker_phrases = [
        "unbounded uncertainty",
        "missing required fact",
        "missing required facts",
        "required facts missing",
        "critical gaps",
    ]
    for leg in ["true", "north", "aligned"]:
        leg_path = base_dir / "02_analysis" / f"{leg}.md"
        if not leg_path.is_file():
            blockers.append(f"{leg}.md missing")
            continue
        content = leg_path.read_text(encoding="utf-8")
        content_n = normalize_text(content)
        status_match = re.search(
            r"^\s*status\s*:\s*(pass|pause|fail)\b",
            content_n,
            flags=re.IGNORECASE | re.MULTILINE,
        )
        if status_match and status_match.group(1).lower() != "pass":
            blockers.append(f"{leg}.md status {status_match.group(1).lower()}")
        for phrase in marker_phrases:
            if phrase_present(content_n, phrase):
                blockers.append(f"{leg}.md contains '{phrase}'")
                break
    return blockers


def gate_orchestration(base_dir):
    engine = OrchestrationEngine(base_dir)
    status = engine.evaluate()
    if not status.valid:
        return GateResult(
            "O",
            "Orchestration state order",
            False,
            "; ".join(status.violations),
        )
    if status.stage == "uninitialized":
        return GateResult(
            "O",
            "Orchestration state order",
            False,
            "intake artifacts are incomplete",
        )
    return GateResult("O", "Orchestration state order", True, f"OK ({status.stage})")


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


def gate_decision_state(base_dir):
    required = ["Decision State", "What This Memo Does Not Say"]
    memo_files = find_memo_files(base_dir)
    if not memo_files:
        return GateResult("B", "Decision state validity", False, "No memo files found")
    failures = []
    for memo in memo_files:
        content = memo.read_text(encoding="utf-8")
        missing = has_sections(content, required)
        if missing:
            failures.append(f"{memo.name} missing {', '.join(missing)}")
            continue
        states = parse_decision_states(content)
        if len(states) != 1:
            failures.append(
                f"{memo.name} must select exactly one decision state (found {len(states)})"
            )
            continue
        state = states[0]
        if state == "Pause" and not section_has_list_items(content, "Missing Information List"):
            failures.append(
                f"{memo.name} Pause requires 'Missing Information List' with list items"
            )
        if state == "Avoid" and not section_has_content(content, "Rationale Summary"):
            failures.append(f"{memo.name} Avoid requires non-empty 'Rationale Summary'")
        if state == "Proceed":
            blockers = proceed_blockers(base_dir)
            if blockers:
                failures.append(
                    f"{memo.name} Proceed invalid due to kernel blockers: {', '.join(blockers)}"
                )
    if failures:
        return GateResult("B", "Decision state validity", False, "; ".join(failures))
    return GateResult("B", "Decision state validity", True, "OK")


def load_language_rules():
    rules_path = ROOT / "00_governance" / "LANGUAGE_RULES.yml"
    data = parse_simple_yaml(rules_path)
    forbidden = data.get("forbidden_terms", []) or []
    required_sections = data.get("required_sections", []) or []
    required_phrases = data.get("required_phrases", []) or []
    return forbidden, required_sections, required_phrases


def gate_language(base_dir):
    memo_files = find_memo_files(base_dir)
    if not memo_files:
        return GateResult("C", "Language lint", False, "No memo files found")
    forbidden, required_sections, required_phrases = load_language_rules()
    violations = []
    missing_sections = {}
    missing_phrases = {}
    for memo in memo_files:
        content = memo.read_text(encoding="utf-8")
        bad_terms = [term for term in forbidden if phrase_present(content, term)]
        if bad_terms:
            violations.append(f"{memo.name} contains {', '.join(sorted(set(bad_terms)))}")
        if required_sections:
            missing = has_sections(content, required_sections)
            if missing:
                missing_sections[memo.name] = missing
        if required_phrases:
            missing = [phrase for phrase in required_phrases if not phrase_present(content, phrase)]
            if missing:
                missing_phrases[memo.name] = missing
    if violations or missing_sections or missing_phrases:
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
        if missing_phrases:
            details.append(
                "; ".join(
                    f"{name} missing phrases {', '.join(phrases)}"
                    for name, phrases in sorted(missing_phrases.items())
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
        size = entry.get("size")
        mtime = entry.get("mtime")
        if not path or not sha256 or size is None or mtime is None:
            return GateResult("D", "Packaging integrity", False, "manifest entry missing fields")
        manifest_map[path] = {"sha256": sha256, "size": int(size), "mtime": int(mtime)}
    missing_files = [rel for rel in ALLOWLIST_FILES if not (base_dir / rel).is_file()]
    if missing_files:
        return GateResult(
            "D", "Packaging integrity", False, "missing: " + ", ".join(missing_files)
        )
    missing_entries = [rel for rel in ALLOWLIST_FILES if rel not in manifest_map]
    if missing_entries:
        return GateResult(
            "D", "Packaging integrity", False, "missing: " + ", ".join(missing_entries)
        )
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
        if path == "04_package/manifest.json":
            continue
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
        gate_orchestration(base_dir),
        gate_kernel(),
        gate_decision_state(base_dir),
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
        "- [ ] Proceed\n"
        "- [x] Pause\n"
        "- [ ] Avoid / Walk Away\n\n"
        "## Missing Information List\n"
        "- Add required facts and evidence before final decision.\n\n"
        "## What This Memo Does Not Say\n"
        "- It does not commit to outcomes or timelines.\n"
        "- It does not provide licensed professional advice.\n"
        "- Non-representational advisory only.\n",
        encoding="utf-8",
    )
    write_manifest(base_dir)
    print(f"Initialized client: {slug}")


def cmd_validate(slug, base_dir=None):
    if base_dir is None:
        validate_slug(slug)
        base_dir = slug_path(slug)
    if not base_dir.is_dir():
        print(f"ERROR: Client slug not found: {slug}", file=sys.stderr)
        return 2, []
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
    gate_report_path = base_dir / "04_package" / "gate_report.json"
    if not gate_report_path.is_file():
        gate_report_path.parent.mkdir(parents=True, exist_ok=True)
        gate_report_path.write_text("{}", encoding="utf-8")
    write_manifest(base_dir)
    exit_code, results = cmd_validate(slug, base_dir=base_dir)
    write_gate_report(base_dir, slug, results)
    write_manifest(base_dir)
    if exit_code != 0:
        print("RUN: BLOCKED (package stage requires all gates to pass)")
        sys.exit(exit_code)
    engine = OrchestrationEngine(base_dir)
    try:
        engine.require_package_allowed(results)
    except OrchestrationError as exc:
        print(f"ERROR: Package stage blocked by orchestration: {exc}", file=sys.stderr)
        sys.exit(1)
    run_timestamp = datetime.now(timezone.utc)
    run_dir = ROOT / "runs" / run_timestamp.strftime(f"%Y%m%d_{slug}_%H%M%SZ")
    run_dir.mkdir(parents=True, exist_ok=True)
    manifest_src = base_dir / "04_package" / "manifest.json"
    gate_report_src = base_dir / "04_package" / "gate_report.json"
    manifest_dst = run_dir / "manifest.json"
    gate_report_dst = run_dir / "gate_report.json"
    shutil.copy2(manifest_src, manifest_dst)
    shutil.copy2(gate_report_src, gate_report_dst)
    generated_at = run_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
    status = "pass" if exit_code == 0 else "fail"
    build_log_path = run_dir / "build_log.txt"
    build_log_path.write_text(f"{generated_at} {status}\n", encoding="utf-8")
    record = {
        "slug": slug,
        "generated_at": generated_at,
        "status": status,
        "manifest": manifest_dst.resolve().as_posix(),
        "gate_report": gate_report_dst.resolve().as_posix(),
        "build_log": build_log_path.resolve().as_posix(),
    }
    record_path = run_dir / "run_record.json"
    write_json(record_path, record)


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
