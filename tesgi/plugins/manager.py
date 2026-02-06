"""Allowlisted plugin loader and runtime dispatch manager."""

from __future__ import annotations

import importlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

from .interfaces import PLUGIN_TYPES, EvalPlugin, LLMGatewayPlugin, PolicyFinding, PolicyPlugin, TelemetryPlugin, WorkflowPlugin


class PluginConfigError(RuntimeError):
    pass


@dataclass(frozen=True)
class PluginSpec:
    plugin_id: str
    plugin_type: str
    module: str
    class_name: str
    version: str
    enabled_by_default: bool = False


def _normalize_enabled_ids(enabled_plugin_ids: Sequence[str] | None) -> tuple[str, ...] | None:
    if enabled_plugin_ids is None:
        return None
    normalized = []
    for plugin_id in enabled_plugin_ids:
        value = plugin_id.strip()
        if not value:
            continue
        normalized.append(value)
    if not normalized:
        return tuple()
    unique = []
    for value in normalized:
        if value not in unique:
            unique.append(value)
    return tuple(unique)


def load_allowlist(path: Path) -> dict[str, PluginSpec]:
    if not path.is_file():
        raise PluginConfigError(f"Plugin allowlist file not found: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PluginConfigError(f"Plugin allowlist JSON is invalid: {exc}") from exc
    plugins = payload.get("plugins")
    if not isinstance(plugins, list):
        raise PluginConfigError("Plugin allowlist must define 'plugins' as a list")
    specs: dict[str, PluginSpec] = {}
    for item in plugins:
        if not isinstance(item, dict):
            raise PluginConfigError("Plugin allowlist entries must be objects")
        plugin_id = item.get("id")
        plugin_type = item.get("type")
        module = item.get("module")
        class_name = item.get("class")
        version = item.get("version")
        enabled_by_default = bool(item.get("enabled_by_default", False))
        if not all(isinstance(v, str) and v.strip() for v in [plugin_id, plugin_type, module, class_name, version]):
            raise PluginConfigError("Plugin allowlist entry has missing or invalid fields")
        if plugin_type not in PLUGIN_TYPES:
            raise PluginConfigError(f"Plugin type is not recognized: {plugin_type}")
        if plugin_id in specs:
            raise PluginConfigError(f"Duplicate plugin id in allowlist: {plugin_id}")
        specs[plugin_id] = PluginSpec(
            plugin_id=plugin_id,
            plugin_type=plugin_type,
            module=module,
            class_name=class_name,
            version=version,
            enabled_by_default=enabled_by_default,
        )
    return specs


def resolve_specs(
    allowlist_specs: dict[str, PluginSpec],
    enabled_plugin_ids: Sequence[str] | None,
) -> list[PluginSpec]:
    normalized = _normalize_enabled_ids(enabled_plugin_ids)
    if normalized is None:
        selected = [spec for spec in allowlist_specs.values() if spec.enabled_by_default]
        return sorted(selected, key=lambda spec: spec.plugin_id)
    if "all" in normalized:
        return sorted(allowlist_specs.values(), key=lambda spec: spec.plugin_id)
    selected: list[PluginSpec] = []
    for plugin_id in normalized:
        spec = allowlist_specs.get(plugin_id)
        if spec is None:
            known = ", ".join(sorted(allowlist_specs.keys()))
            raise PluginConfigError(f"Plugin id is not allowlisted: {plugin_id} (known: {known})")
        selected.append(spec)
    return selected


def instantiate_plugin(spec: PluginSpec) -> Any:
    try:
        module = importlib.import_module(spec.module)
    except ImportError as exc:
        raise PluginConfigError(f"Failed to import plugin module for {spec.plugin_id}: {exc}") from exc
    try:
        cls = getattr(module, spec.class_name)
    except AttributeError as exc:
        raise PluginConfigError(
            f"Plugin class not found for {spec.plugin_id}: {spec.module}.{spec.class_name}"
        ) from exc
    instance = cls()
    plugin_type = getattr(instance, "plugin_type", None)
    version = getattr(instance, "version", None)
    if plugin_type != spec.plugin_type:
        raise PluginConfigError(
            f"Plugin type mismatch for {spec.plugin_id}: expected {spec.plugin_type}, got {plugin_type}"
        )
    if version != spec.version:
        raise PluginConfigError(
            f"Plugin version mismatch for {spec.plugin_id}: expected {spec.version}, got {version}"
        )
    return instance


class PluginManager:
    def __init__(self, instances: Iterable[Any] = ()):
        self._workflow: list[WorkflowPlugin] = []
        self._policy: list[PolicyPlugin] = []
        self._llm: list[LLMGatewayPlugin] = []
        self._telemetry: list[TelemetryPlugin] = []
        self._eval: list[EvalPlugin] = []
        for instance in instances:
            plugin_type = getattr(instance, "plugin_type", "")
            if plugin_type == "workflow_plugin":
                self._workflow.append(instance)
            elif plugin_type == "policy_plugin":
                self._policy.append(instance)
            elif plugin_type == "llm_gateway_plugin":
                self._llm.append(instance)
            elif plugin_type == "telemetry_plugin":
                self._telemetry.append(instance)
            elif plugin_type == "eval_plugin":
                self._eval.append(instance)
            else:
                raise PluginConfigError(f"Unsupported plugin type for instance: {plugin_type}")

    @classmethod
    def from_allowlist(
        cls,
        allowlist_path: Path,
        enabled_plugin_ids: Sequence[str] | None = None,
    ) -> "PluginManager":
        specs = load_allowlist(allowlist_path)
        selected = resolve_specs(specs, enabled_plugin_ids=enabled_plugin_ids)
        instances = [instantiate_plugin(spec) for spec in selected]
        return cls(instances=instances)

    def active_plugins(self) -> list[dict[str, str]]:
        active = []
        for group in [self._workflow, self._policy, self._llm, self._telemetry, self._eval]:
            for plugin in group:
                metadata = plugin.metadata()
                active.append(metadata)
        return sorted(active, key=lambda item: (item["plugin_type"], item["name"]))

    def emit_telemetry(self, event: str, payload: dict[str, Any]) -> None:
        for plugin in self._telemetry:
            plugin.record_event(event, payload)

    def workflow_before_stage(self, stage: str, context: dict[str, Any]) -> None:
        self.emit_telemetry("workflow.before_stage", {"stage": stage, **context})
        for plugin in self._workflow:
            plugin.before_stage(stage, context)

    def workflow_after_stage(self, stage: str, context: dict[str, Any]) -> None:
        for plugin in self._workflow:
            plugin.after_stage(stage, context)
        self.emit_telemetry("workflow.after_stage", {"stage": stage, **context})

    def evaluate_policy(self, context: dict[str, Any]) -> list[PolicyFinding]:
        findings: list[PolicyFinding] = []
        for plugin in self._policy:
            output = plugin.evaluate(context) or []
            for finding in output:
                if isinstance(finding, PolicyFinding):
                    findings.append(finding)
                    continue
                if isinstance(finding, dict):
                    findings.append(
                        PolicyFinding(
                            gate_id=str(finding.get("gate_id", "P-PLUGIN")),
                            name=str(finding.get("name", "Plugin policy")),
                            status=bool(finding.get("status", False)),
                            detail=str(finding.get("detail", "")),
                        )
                    )
                    continue
                raise PluginConfigError("Policy plugin findings must be PolicyFinding or dict")
        if findings:
            self.emit_telemetry(
                "policy.findings",
                {
                    **context,
                    "findings": [
                        {
                            "gate_id": finding.gate_id,
                            "name": finding.name,
                            "status": finding.status,
                            "detail": finding.detail,
                        }
                        for finding in findings
                    ],
                },
            )
        return findings

    def eval_before_case(self, case_path: str, slug: str, context: dict[str, Any]) -> None:
        self.emit_telemetry(
            "eval.before_case",
            {"case_path": case_path, "slug": slug, **context},
        )
        for plugin in self._eval:
            plugin.before_case(case_path, slug, context)

    def eval_after_case(self, case_path: str, slug: str, exit_code: int, context: dict[str, Any]) -> None:
        for plugin in self._eval:
            plugin.after_case(case_path, slug, exit_code, context)
        self.emit_telemetry(
            "eval.after_case",
            {"case_path": case_path, "slug": slug, "exit_code": exit_code, **context},
        )

    def generate_via_llm(self, prompt: str, context: dict[str, Any]) -> dict[str, Any]:
        if not self._llm:
            raise PluginConfigError("No llm_gateway_plugin is enabled")
        return self._llm[0].generate(prompt, context)
