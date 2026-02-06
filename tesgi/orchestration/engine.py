"""Orchestration state engine for TESGI workflow sequencing."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

from .contracts import STAGE_CONTRACTS
from .states import STAGES


class OrchestrationError(RuntimeError):
    pass


@dataclass(frozen=True)
class StageStatus:
    stage: str
    valid: bool
    violations: tuple[str, ...]
    existing_files: tuple[str, ...]
    passed_gates: tuple[str, ...]

    def as_dict(self) -> dict:
        return {
            "stage": self.stage,
            "valid": self.valid,
            "violations": list(self.violations),
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
        return StageStatus(
            stage=stage,
            valid=not violations,
            violations=violations,
            existing_files=self.collect_existing_files(),
            passed_gates=tuple(sorted(set(passed_gates))),
        )

    def require_package_allowed(self, gate_results: Sequence) -> None:
        status = self.evaluate(gate_results=gate_results)
        if not status.valid:
            raise OrchestrationError("; ".join(status.violations))
        required = STAGE_CONTRACTS["package_passed"].required_gates
        missing = [gate for gate in required if gate not in status.passed_gates]
        if missing:
            raise OrchestrationError(
                "package step blocked until required gates pass: " + ", ".join(missing)
            )
