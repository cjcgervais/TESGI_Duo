"""Gate validators and validation orchestration for TESGI."""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_PACKAGERS_DIR = ROOT / "03_tools" / "packagers"
if str(_PACKAGERS_DIR) not in sys.path:
    sys.path.insert(0, str(_PACKAGERS_DIR))

from tesgi.orchestration import OrchestrationEngine
from tesgi_packagers import MANIFEST_REQUIRED_FILES, compute_manifest

KERNEL_REQUIREMENTS = {
    "true.md": {
        "section_groups": [
            ["Source Verification", "Sources"],
            ["Fact Availability", "Facts"],
            ["Boundary Clarity", "Boundaries"],
        ],
        "semantic_sections": {
            "observations": ["Observations"],
            "explicit uncertainties": ["Uncertainties", "Explicit Uncertainties"],
            "risk notes": ["Risk Notes", "Risks"],
        },
        "require_status": True,
    },
    "north.md": {
        "section_groups": [
            ["Regulatory", "Planning"],
            ["Timeline", "Horizon", "Context"],
        ],
        "semantic_sections": {
            "observations": ["Observations"],
            "explicit uncertainties": ["Uncertainties", "Explicit Uncertainties"],
            "risk notes": ["Risk Notes", "Risks"],
        },
        "require_status": True,
    },
    "aligned.md": {
        "section_groups": [
            ["Objectives"],
            ["Constraints", "Constraint", "Assumptions", "Structure"],
        ],
        "semantic_sections": {
            "observations": ["Observations"],
            "explicit uncertainties": ["Uncertainties", "Explicit Uncertainties"],
            "risk notes": ["Risk Notes", "Risks"],
        },
        "require_status": True,
    },
}

BLOCKER_PATTERNS = [
    r"Status:\s*FAIL",
    r"(?i)unbounded\s+uncertainty",
    r"(?i)cannot\s+be\s+verified",
    r"(?i)missing\s+required",
    r"(?i)fundamental\s+misalignment",
    r"(?i)critical\s+gap",
]


@dataclass(frozen=True)
class GateResult:
    gate_id: str
    name: str
    status: bool
    detail: str

    def as_dict(self) -> dict:
        return {
            "id": self.gate_id,
            "name": self.name,
            "status": "pass" if self.status else "fail",
            "detail": self.detail,
        }


def parse_simple_yaml(path: Path) -> dict:
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


def find_memo_files(base_dir: Path) -> list[Path]:
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


def normalize_text(text: str) -> str:
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


def phrase_present(content: str, phrase: str) -> bool:
    phrase = normalize_text(phrase).strip()
    if not phrase:
        return False
    tokens = phrase.split()
    pattern = r"\b" + r"\s+".join(re.escape(token) for token in tokens) + r"\b"
    haystack = normalize_text(content)
    return re.search(pattern, haystack, flags=re.IGNORECASE) is not None


def has_sections(content: str, sections: list[str]) -> list[str]:
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


def extract_section(content: str, section_name: str) -> str:
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


def extract_section_by_aliases(content: str, aliases: list[str]) -> tuple[str | None, str]:
    for alias in aliases:
        section = extract_section(content, alias)
        if section:
            return alias, section
    return None, ""


def parse_decision_state(content: str) -> str | None:
    section = extract_section(content, "Decision State")
    selected = []
    if section:
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
    explicit = re.search(
        r"decision\s*state\s*:\s*(proceed|pause|avoid|walk\s*away)",
        normalize_text(content),
        flags=re.IGNORECASE,
    )
    if explicit:
        value = explicit.group(1).lower().replace(" ", "")
        if value in {"avoid", "walkaway"}:
            selected.append("Avoid")
        elif value == "pause":
            selected.append("Pause")
        else:
            selected.append("Proceed")
    unique = []
    for state in ["Proceed", "Pause", "Avoid"]:
        if state in selected:
            unique.append(state)
    if not unique:
        return None
    if len(unique) > 1:
        return "Multiple"
    return unique[0]


def section_has_list_items(content: str, section_name: str) -> bool:
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


def section_has_content(content: str, section_name: str) -> bool:
    section = extract_section(content, section_name)
    if not section:
        return False
    return section_has_text(section)


def section_has_text(section: str) -> bool:
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


def section_has_list_or_text(section: str) -> bool:
    if not section:
        return False
    if section_has_text(section):
        return True
    return False


def section_has_explicit_uncertainty(section: str) -> bool:
    return section_has_list_or_text(section)


def kernel_has_blockers(base_dir: Path) -> list[str]:
    analysis_dir = base_dir / "02_analysis"
    if not analysis_dir.is_dir():
        return ["02_analysis missing"]
    blockers = []
    for path in sorted(analysis_dir.glob("*.md")):
        content = normalize_text(path.read_text(encoding="utf-8"))
        for pattern in BLOCKER_PATTERNS:
            if re.search(pattern, content, flags=re.IGNORECASE):
                blockers.append(f"{path.name} matched {pattern}")
                break
    return blockers


def file_has_heading_alias(content: str, aliases: list[str]) -> bool:
    for line in content.splitlines():
        line_l = line.strip().lower()
        if not line_l.startswith("#"):
            continue
        for alias in aliases:
            if alias.lower() in line_l:
                return True
    return False


def status_line_present(content: str) -> bool:
    for line in content.splitlines():
        if "status:" in line.lower():
            return True
    return False


def validate_kernel_content(filepath: Path, required_sections: dict) -> list[str]:
    if not filepath.is_file():
        return [f"{filepath.name} missing"]
    content = filepath.read_text(encoding="utf-8")
    errors = []

    section_groups = required_sections.get("section_groups", [])
    for aliases in section_groups:
        if not file_has_heading_alias(content, aliases):
            errors.append(f"{filepath.name} missing section ({' / '.join(aliases)})")

    semantic_sections = required_sections.get("semantic_sections", {})
    for semantic_name, aliases in semantic_sections.items():
        matched_alias, section = extract_section_by_aliases(content, aliases)
        if matched_alias is None:
            errors.append(f"{filepath.name} missing semantic section ({semantic_name})")
            continue
        if not section_has_list_or_text(section):
            errors.append(
                f"{filepath.name} semantic section '{semantic_name}' is empty"
            )
            continue
        if semantic_name == "explicit uncertainties" and not section_has_explicit_uncertainty(section):
            errors.append(
                f"{filepath.name} semantic section '{semantic_name}' must state uncertainty explicitly"
            )

    if required_sections.get("require_status", False) and not status_line_present(content):
        errors.append(f"{filepath.name} missing Status line")

    return errors


def gate_orchestration(base_dir: Path) -> GateResult:
    engine = OrchestrationEngine(base_dir)
    status = engine.evaluate()
    if not status.valid:
        details = list(status.violations) + list(status.schema_errors)
        return GateResult(
            "O",
            "Orchestration state order",
            False,
            "; ".join(details),
        )
    if status.stage == "uninitialized":
        return GateResult(
            "O",
            "Orchestration state order",
            False,
            "intake artifacts are incomplete",
        )
    return GateResult("O", "Orchestration state order", True, f"OK ({status.stage})")


def gate_kernel(base_dir: Path) -> GateResult:
    analysis_dir = base_dir / "02_analysis"
    if not analysis_dir.is_dir():
        return GateResult("A", "Kernel completeness", False, "02_analysis missing")
    failures = []
    for filename, requirements in KERNEL_REQUIREMENTS.items():
        filepath = analysis_dir / filename
        failures.extend(validate_kernel_content(filepath, requirements))
    if failures:
        return GateResult("A", "Kernel completeness", False, "; ".join(failures))
    return GateResult("A", "Kernel completeness", True, "OK")


def gate_decision_state(base_dir: Path) -> GateResult:
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
        state = parse_decision_state(content)
        if state is None:
            failures.append(f"{memo.name} has no decision state marked")
            continue
        if state == "Multiple":
            failures.append(f"{memo.name} has multiple decision states marked")
            continue
        if state == "Pause" and not section_has_list_items(content, "Missing Information List"):
            failures.append(
                f"{memo.name} Pause requires 'Missing Information List' with list items"
            )
        if state == "Avoid" and not section_has_content(content, "Rationale Summary"):
            failures.append(f"{memo.name} Avoid requires non-empty 'Rationale Summary'")
        if state == "Proceed":
            blockers = kernel_has_blockers(base_dir)
            if blockers:
                failures.append(
                    f"{memo.name} Proceed invalid due to kernel blockers: {', '.join(blockers)}"
                )
    if failures:
        return GateResult("B", "Decision state validity", False, "; ".join(failures))
    return GateResult("B", "Decision state validity", True, "OK")


def load_language_rules() -> tuple[list[str], list[str], list[str]]:
    rules_path = ROOT / "00_governance" / "LANGUAGE_RULES.yml"
    data = parse_simple_yaml(rules_path)
    forbidden = data.get("forbidden_terms", []) or []
    required_sections = data.get("required_sections", []) or []
    required_phrases = data.get("required_phrases", []) or []
    return forbidden, required_sections, required_phrases


def gate_language(base_dir: Path) -> GateResult:
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


def _manifest_metadata_ok(manifest: dict) -> tuple[bool, str]:
    for key in ["generated_at", "base_dir", "tesgi_version", "python_version", "tooling"]:
        if key not in manifest:
            return False, f"manifest.json missing metadata field: {key}"
    tooling = manifest.get("tooling")
    if not isinstance(tooling, dict):
        return False, "manifest.json tooling must be an object"
    if not tooling.get("cli"):
        return False, "manifest.json tooling.cli is required"
    if not tooling.get("command"):
        return False, "manifest.json tooling.command is required"
    return True, ""


def gate_manifest(base_dir: Path) -> GateResult:
    manifest_path = base_dir / "04_package" / "manifest.json"
    if not manifest_path.is_file():
        return GateResult("D", "Packaging integrity", False, "manifest.json missing")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return GateResult("D", "Packaging integrity", False, f"manifest.json invalid: {exc}")

    meta_ok, meta_detail = _manifest_metadata_ok(manifest)
    if not meta_ok:
        return GateResult("D", "Packaging integrity", False, meta_detail)

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
        manifest_map[path] = {
            "sha256": str(sha256),
            "size": int(size),
            "mtime": int(mtime),
        }

    missing_files = [rel for rel in MANIFEST_REQUIRED_FILES if not (base_dir / rel).is_file()]
    if missing_files:
        return GateResult(
            "D",
            "Packaging integrity",
            False,
            "missing artifacts: " + ", ".join(missing_files),
        )

    missing_entries = [rel for rel in MANIFEST_REQUIRED_FILES if rel not in manifest_map]
    if missing_entries:
        return GateResult(
            "D",
            "Packaging integrity",
            False,
            "manifest entries missing: " + ", ".join(missing_entries),
        )

    expected = compute_manifest(
        base_dir,
        command_name=str(manifest.get("tooling", {}).get("command", "package")),
    )["files"]
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


def gate_sources(base_dir: Path) -> GateResult:
    manifest_path = base_dir / "01_sources" / "sources_manifest.json"
    if not manifest_path.is_file():
        return GateResult("E", "Sources manifest", False, "01_sources/sources_manifest.json missing")
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return GateResult("E", "Sources manifest", False, f"sources_manifest.json invalid: {exc}")
    sources = payload.get("sources")
    if not isinstance(sources, list) or not sources:
        return GateResult("E", "Sources manifest", False, "sources must contain at least one entry")
    for idx, entry in enumerate(sources, start=1):
        if not isinstance(entry, dict):
            return GateResult("E", "Sources manifest", False, f"source {idx} must be an object")
        missing = [field for field in ["id", "type", "tier", "description"] if not entry.get(field)]
        if missing:
            return GateResult(
                "E",
                "Sources manifest",
                False,
                f"source {idx} missing required fields: {', '.join(missing)}",
            )
    return GateResult("E", "Sources manifest", True, "OK")


def run_gates(base_dir: Path, slug: str, plugin_manager=None, plugin_runtime_context=None) -> list[GateResult]:
    results = [
        gate_orchestration(base_dir),
        gate_kernel(base_dir),
        gate_decision_state(base_dir),
        gate_language(base_dir),
        gate_manifest(base_dir),
        gate_sources(base_dir),
    ]
    if plugin_manager is not None and plugin_runtime_context is not None:
        context = plugin_runtime_context(slug, base_dir)
        context["core_gate_results"] = [result.as_dict() for result in results]
        findings = plugin_manager.evaluate_policy(context)
        for idx, finding in enumerate(findings, start=1):
            gate_id = finding.gate_id.strip() if finding.gate_id.strip() else f"P{idx}"
            results.append(GateResult(gate_id, finding.name, finding.status, finding.detail))
    return results


def print_results(results: list[GateResult]) -> None:
    for result in results:
        status = "PASS" if result.status else "FAIL"
        print(f"{result.gate_id} {status}: {result.name} - {result.detail}")
