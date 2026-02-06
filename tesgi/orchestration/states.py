"""Canonical orchestration stages and transition helpers."""

from __future__ import annotations

from typing import Final

STAGES: Final[tuple[str, ...]] = (
    "intake_ready",
    "true_complete",
    "north_complete",
    "aligned_complete",
    "decision_synthesized",
    "memo_built",
    "boundary_passed",
    "package_passed",
    "eval_passed",
)

STAGE_INDEX: Final[dict[str, int]] = {stage: idx for idx, stage in enumerate(STAGES)}

PREDECESSOR: Final[dict[str, str | None]] = {STAGES[0]: None}
for idx in range(1, len(STAGES)):
    PREDECESSOR[STAGES[idx]] = STAGES[idx - 1]

NEXT_STAGE: Final[dict[str, str | None]] = {STAGES[-1]: None}
for idx in range(len(STAGES) - 1):
    NEXT_STAGE[STAGES[idx]] = STAGES[idx + 1]


def is_known_stage(stage: str) -> bool:
    return stage in STAGE_INDEX


def stage_rank(stage: str) -> int:
    if stage not in STAGE_INDEX:
        raise ValueError(f"Unknown stage: {stage}")
    return STAGE_INDEX[stage]


def can_transition(current_stage: str, target_stage: str) -> bool:
    if not is_known_stage(current_stage) or not is_known_stage(target_stage):
        return False
    return stage_rank(target_stage) == stage_rank(current_stage) + 1


def has_reached(current_stage: str, required_stage: str) -> bool:
    if not is_known_stage(current_stage) or not is_known_stage(required_stage):
        return False
    return stage_rank(current_stage) >= stage_rank(required_stage)
