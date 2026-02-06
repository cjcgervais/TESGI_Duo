"""Reference plugin implementations used by allowlisted plugin specs."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .interfaces import EvalPlugin, LLMGatewayPlugin, PolicyFinding, PolicyPlugin, TelemetryPlugin, WorkflowPlugin


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class NoOpWorkflowPlugin(WorkflowPlugin):
    name = "noop_workflow"
    version = "1.0.0"


class NoOpPolicyPlugin(PolicyPlugin):
    name = "noop_policy"
    version = "1.0.0"


class NoOpLLMGatewayPlugin(LLMGatewayPlugin):
    name = "noop_llm"
    version = "1.0.0"


class JsonlTelemetryPlugin(TelemetryPlugin):
    name = "jsonl_telemetry"
    version = "1.0.0"

    def record_event(self, event: str, payload: dict[str, Any]) -> None:
        telemetry_log_path = payload.get("telemetry_log_path")
        if not telemetry_log_path:
            return
        path = Path(str(telemetry_log_path))
        path.parent.mkdir(parents=True, exist_ok=True)
        event_payload = dict(payload)
        event_payload.pop("telemetry_log_path", None)
        record = {
            "generated_at": utc_now(),
            "event": event,
            "payload": event_payload,
        }
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True, ensure_ascii=True) + "\n")


class NoOpEvalPlugin(EvalPlugin):
    name = "noop_eval"
    version = "1.0.0"


class RequireSourcesManifestPolicyPlugin(PolicyPlugin):
    """
    Reference policy plugin that enforces presence of sources manifest.

    Keep disabled by default; this is intentionally stricter than current golden cases.
    """

    name = "require_sources_manifest"
    version = "1.0.0"

    def evaluate(self, context: dict[str, Any]) -> list[PolicyFinding]:
        base_dir_value = context.get("base_dir")
        if not base_dir_value:
            return [
                PolicyFinding(
                    gate_id="P-SRC",
                    name="Sources manifest policy",
                    status=False,
                    detail="base_dir missing from plugin context",
                )
            ]
        path = Path(str(base_dir_value)) / "01_sources" / "sources_manifest.json"
        if path.is_file():
            return [
                PolicyFinding(
                    gate_id="P-SRC",
                    name="Sources manifest policy",
                    status=True,
                    detail="OK",
                )
            ]
        return [
            PolicyFinding(
                gate_id="P-SRC",
                name="Sources manifest policy",
                status=False,
                detail="01_sources/sources_manifest.json missing",
            )
        ]
