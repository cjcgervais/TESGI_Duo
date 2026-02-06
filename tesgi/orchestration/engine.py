"""Orchestration state engine for TESGI workflow sequencing."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

from .contracts import STAGE_CONTRACTS, STAGE_SCHEMAS
from .states import STAGES


class OrchestrationError(RuntimeError):
    pass


@dataclass(frozen=True)
class StageStatus:
    stage: str
    valid: bool
    violations: tuple[str, ...]
    schema_errors: tuple[str, ...]
    existing_files: tuple[str, ...]
    passed_gates: tuple[str, ...]

    def as_dict(self) -> dict:
        return {
            "stage": self.stage,
            "valid": self.valid,
            "violations": list(self.violations),
            "schema_errors": list(self.schema_errors),
            "existing_files": list(self.existing_files),
            "passed_gates": list(self.passed_gates),
        }


class OrchestrationEngine:
    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)

    def _memo_path(self) -> Path:
        return self.base_dir / "03_memo" / "Decision_Memo.md"

    def _extract_section(self, content: str, section_name: str) -> str:
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

    def _memo_has_decision_state(self) -> bool:
        memo = self._memo_path()
        if not memo.is_file():
            return False
        content = memo.read_text(encoding="utf-8")
        section = self._extract_section(content, "Decision State")
        if section:
            selected = 0
            for raw_line in section.splitlines():
                line = raw_line.strip().lower()
                if not line:
                    continue
                if "[x]" not in line and "\u2611" not in raw_line:
                    continue
                if "proceed" in line or "pause" in line or "avoid" in line or "walk away" in line:
                    selected += 1
            if selected == 1:
                return True
        explicit = re.search(
            r"decision\s*state\s*:\s*(proceed|pause|avoid|walk\s*away)",
            content,
            flags=re.IGNORECASE,
        )
        return explicit is not None

    def _memo_has_required_section(self, section_name: str) -> bool:
        memo = self._memo_path()
        if not memo.is_file():
            return False
        content = memo.read_text(encoding="utf-8")
        return bool(self._extract_section(content, section_name))

    def validate_stage_order(self) -> list[str]:
        violations = []
        true_path = self.base_dir / "02_analysis" / "true.md"
        north_path = self.base_dir / "02_analysis" / "north.md"
        aligned_path = self.base_dir / "02_analysis" / "aligned.md"
        memo_path = self._memo_path()
        manifest_path = self.base_dir / "04_package" / "manifest.json"
        gate_report_path = self.base_dir / "04_package" / "gate_report.json"

        if north_path.is_file() and not true_path.is_file():
            violations.append("north_complete requires 02_analysis/true.md")
        if aligned_path.is_file() and not north_path.is_file():
            violations.append("aligned_complete requires 02_analysis/north.md")
        if memo_path.is_file() and not aligned_path.is_file():
            violations.append("decision_synthesized requires 02_analysis/aligned.md")
        if gate_report_path.is_file() and not manifest_path.is_file():
            violations.append("package artifacts require 04_package/manifest.json")
        return violations

    def collect_existing_files(self) -> tuple[str, ...]:
        known_files = set()
        for contract in STAGE_CONTRACTS.values():
            known_files.update(contract.required_files)
        existing = sorted(rel for rel in known_files if (self.base_dir / rel).is_file())
        return tuple(existing)

    def infer_stage(self, passed_gates: Iterable[str] = ()) -> str:
        passed_gate_set = set(passed_gates)
        existing_files = set(self.collect_existing_files())
        last = "uninitialized"

        for stage in STAGES:
            contract = STAGE_CONTRACTS[stage]
            files_ok = all(rel in existing_files for rel in contract.required_files)
            gates_ok = all(gate in passed_gate_set for gate in contract.required_gates)
            if not files_ok or not gates_ok:
                break
            if stage == "decision_synthesized" and not self._memo_has_decision_state():
                break
            if stage == "memo_built" and not self._memo_has_required_section(
                "What This Memo Does Not Say"
            ):
                break
            last = stage
        return last

    def _validate_stage_schema(self, stage: str, payload: dict) -> tuple[str, ...]:
        schema = STAGE_SCHEMAS.get(stage)
        if schema is None:
            return (f"no stage schema registered for {stage}",)

        errors: list[str] = []
        for key in schema.get("required", []):
            if key not in payload:
                errors.append(f"{stage} schema missing required field: {key}")

        stage_const = schema.get("properties", {}).get("stage", {}).get("const")
        if stage_const and payload.get("stage") != stage_const:
            errors.append(f"{stage} schema requires stage={stage_const}")

        existing = payload.get("existing_files")
        passed = payload.get("passed_gates")
        if not isinstance(existing, list):
            errors.append(f"{stage} schema requires existing_files as list")
        if not isinstance(passed, list):
            errors.append(f"{stage} schema requires passed_gates as list")

        for clause in schema.get("allOf", []):
            properties = clause.get("properties", {})
            existing_rule = properties.get("existing_files", {}).get("contains", {}).get("const")
            if existing_rule and existing_rule not in payload.get("existing_files", []):
                errors.append(f"{stage} schema missing file: {existing_rule}")
            gate_rule = properties.get("passed_gates", {}).get("contains", {}).get("const")
            if gate_rule and gate_rule not in payload.get("passed_gates", []):
                errors.append(f"{stage} schema missing gate: {gate_rule}")

        return tuple(errors)

    def evaluate(self, gate_results: Sequence | None = None) -> StageStatus:
        passed_gates = ()
        if gate_results is not None:
            passed_gates = tuple(
                result.gate_id
                for result in gate_results
                if getattr(result, "status", False) and hasattr(result, "gate_id")
            )
        violations = tuple(self.validate_stage_order())
        stage = self.infer_stage(passed_gates=passed_gates)
        payload = {
            "stage": stage,
            "existing_files": list(self.collect_existing_files()),
            "passed_gates": sorted(set(passed_gates)),
        }
        schema_errors: tuple[str, ...] = ()
        if stage != "uninitialized":
            schema_errors = self._validate_stage_schema(stage, payload)
        return StageStatus(
            stage=stage,
            valid=not violations and not schema_errors,
            violations=violations,
            schema_errors=schema_errors,
            existing_files=tuple(payload["existing_files"]),
            passed_gates=tuple(payload["passed_gates"]),
        )

    def require_package_allowed(self, gate_results: Sequence) -> None:
        status = self.evaluate(gate_results=gate_results)
        if not status.valid:
            details = list(status.violations) + list(status.schema_errors)
            raise OrchestrationError("; ".join(details))
        required = STAGE_CONTRACTS["package_passed"].required_gates
        missing = [gate for gate in required if gate not in status.passed_gates]
        if missing:
            raise OrchestrationError(
                "package step blocked until required gates pass: " + ", ".join(missing)
            )
