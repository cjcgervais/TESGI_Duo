"""Stage contracts and JSON-schema definitions for orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from .states import STAGES


@dataclass(frozen=True)
class StageContract:
    stage: str
    required_files: tuple[str, ...] = ()
    required_gates: tuple[str, ...] = ()


_INTAKE_FILES = (
    "00_intake/intake.md",
    "00_intake/intake_ack.json",
)
_ANALYSIS_FILES = (
    "02_analysis/true.md",
    "02_analysis/north.md",
    "02_analysis/aligned.md",
)
_MEMO_FILE = ("03_memo/Decision_Memo.md",)
_MEMO_BUILD_FILES = (
    "03_memo/Decision_Memo.md",
    "03_memo/memo.md",
)
_PACKAGE_FILES = (
    "04_package/memo.pdf",
    "04_package/invoice.pdf",
    "04_package/receipt.pdf",
    "04_package/manifest.json",
    "04_package/gate_report.json",
    "04_package/runlog.jsonl",
)

STAGE_CONTRACTS: Final[dict[str, StageContract]] = {
    "intake_ready": StageContract(
        stage="intake_ready",
        required_files=_INTAKE_FILES,
    ),
    "true_complete": StageContract(
        stage="true_complete",
        required_files=_INTAKE_FILES + (_ANALYSIS_FILES[0],),
    ),
    "north_complete": StageContract(
        stage="north_complete",
        required_files=_INTAKE_FILES + _ANALYSIS_FILES[:2],
    ),
    "aligned_complete": StageContract(
        stage="aligned_complete",
        required_files=_INTAKE_FILES + _ANALYSIS_FILES,
    ),
    "decision_synthesized": StageContract(
        stage="decision_synthesized",
        required_files=_INTAKE_FILES + _ANALYSIS_FILES + _MEMO_FILE,
    ),
    "memo_built": StageContract(
        stage="memo_built",
        required_files=_INTAKE_FILES + _ANALYSIS_FILES + _MEMO_BUILD_FILES,
    ),
    "boundary_passed": StageContract(
        stage="boundary_passed",
        required_files=_INTAKE_FILES + _ANALYSIS_FILES + _MEMO_BUILD_FILES,
        required_gates=("O", "A", "B", "C", "E"),
    ),
    "package_passed": StageContract(
        stage="package_passed",
        required_files=_INTAKE_FILES + _ANALYSIS_FILES + _MEMO_BUILD_FILES + _PACKAGE_FILES,
        required_gates=("O", "A", "B", "C", "D", "E"),
    ),
    "eval_passed": StageContract(
        stage="eval_passed",
        required_files=_INTAKE_FILES + _ANALYSIS_FILES + _MEMO_BUILD_FILES + _PACKAGE_FILES,
        required_gates=("O", "A", "B", "C", "D", "E"),
    ),
}


def build_stage_schema(contract: StageContract) -> dict:
    all_of = []
    for rel_path in contract.required_files:
        all_of.append(
            {
                "properties": {
                    "existing_files": {"contains": {"const": rel_path}},
                }
            }
        )
    for gate_id in contract.required_gates:
        all_of.append(
            {
                "properties": {
                    "passed_gates": {"contains": {"const": gate_id}},
                }
            }
        )

    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"tesgi.orchestration.{contract.stage}",
        "title": f"{contract.stage} contract",
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "stage": {"const": contract.stage},
            "existing_files": {
                "type": "array",
                "items": {"type": "string"},
            },
            "passed_gates": {
                "type": "array",
                "items": {"type": "string"},
            },
        },
        "required": ["stage", "existing_files", "passed_gates"],
        "allOf": all_of,
    }


STAGE_SCHEMAS: Final[dict[str, dict]] = {
    stage: build_stage_schema(STAGE_CONTRACTS[stage]) for stage in STAGES
}
