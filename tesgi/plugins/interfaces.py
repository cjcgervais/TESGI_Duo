"""Plugin interfaces for controlled TESGI extensibility."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final

PLUGIN_TYPES: Final[tuple[str, ...]] = (
    "workflow_plugin",
    "policy_plugin",
    "llm_gateway_plugin",
    "telemetry_plugin",
    "eval_plugin",
)


class BasePlugin:
    """Base metadata contract shared by all plugins."""

    name = "base_plugin"
    version = "0.0.0"
    plugin_type = "base"

    def metadata(self) -> dict[str, str]:
        return {
            "name": self.name,
            "version": self.version,
            "plugin_type": self.plugin_type,
        }


@dataclass(frozen=True)
class PolicyFinding:
    gate_id: str
    name: str
    status: bool
    detail: str


class WorkflowPlugin(BasePlugin):
    plugin_type = "workflow_plugin"

    def before_stage(self, stage: str, context: dict[str, Any]) -> None:
        return None

    def after_stage(self, stage: str, context: dict[str, Any]) -> None:
        return None


class PolicyPlugin(BasePlugin):
    plugin_type = "policy_plugin"

    def evaluate(self, context: dict[str, Any]) -> list[PolicyFinding]:
        return []


class LLMGatewayPlugin(BasePlugin):
    plugin_type = "llm_gateway_plugin"

    def generate(self, prompt: str, context: dict[str, Any]) -> dict[str, Any]:
        return {
            "provider": "noop",
            "model": "noop",
            "response": "",
            "prompt": prompt,
            "context": context,
        }


class TelemetryPlugin(BasePlugin):
    plugin_type = "telemetry_plugin"

    def record_event(self, event: str, payload: dict[str, Any]) -> None:
        return None


class EvalPlugin(BasePlugin):
    plugin_type = "eval_plugin"

    def before_case(self, case_path: str, slug: str, context: dict[str, Any]) -> None:
        return None

    def after_case(self, case_path: str, slug: str, exit_code: int, context: dict[str, Any]) -> None:
        return None
