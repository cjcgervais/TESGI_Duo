# TESGI Plugin Interfaces

This folder documents controlled plugin extensibility for TESGI.

## Plugin Types

- `workflow_plugin`: receives stage lifecycle hooks.
- `policy_plugin`: returns additional policy findings.
- `llm_gateway_plugin`: optional model routing adapter.
- `telemetry_plugin`: records run/eval events.
- `eval_plugin`: hooks around evaluation case execution.

## Governance Controls

- Allowlist file: `00_governance/PLUGIN_ALLOWLIST.json`
- Each plugin entry is pinned to:
  - `id`
  - `type`
  - `module`
  - `class`
  - `version`
- Runtime loading fails if:
  - plugin id is not allowlisted
  - plugin type mismatches the allowlist
  - plugin version mismatches the allowlist

## Enable/Disable Per Run

Use `--plugins` on `validate`, `run`, or `eval`:

```powershell
python -m tesgi validate demo --plugins noop_workflow,noop_policy
python -m tesgi run demo --plugins jsonl_telemetry
python -m tesgi eval --plugins all
```

- Omit `--plugins` to run with no plugins enabled.
- `--plugins all` enables all allowlisted plugins.
- `require_sources_manifest` is a strict policy reference plugin and can fail runs when
  `01_sources/sources_manifest.json` is not present.

## Reference Implementations

Reference plugins are in `tesgi/plugins/reference.py`:

- `NoOpWorkflowPlugin`
- `NoOpPolicyPlugin`
- `RequireSourcesManifestPolicyPlugin` (strict, disabled by default)
- `NoOpLLMGatewayPlugin`
- `JsonlTelemetryPlugin`
- `NoOpEvalPlugin`

These are baseline implementations intended for extension.
