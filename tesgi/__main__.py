import argparse
import os
import shutil
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from .orchestration import OrchestrationEngine, OrchestrationError
from .plugins import PluginConfigError, PluginManager

ROOT = Path(__file__).resolve().parents[1]
VALIDATORS_DIR = ROOT / "03_tools" / "validators"
PACKAGERS_DIR = ROOT / "03_tools" / "packagers"
for tools_dir in (PACKAGERS_DIR, VALIDATORS_DIR):
    if str(tools_dir) not in sys.path:
        sys.path.insert(0, str(tools_dir))

from tesgi_gate_validators import print_results, run_gates
from tesgi_packagers import (
    append_runlog_event,
    build_memo_artifacts,
    initialize_package_skeleton,
    utc_now,
    write_gate_report,
    write_json,
    write_manifest,
)


def validate_slug(slug):
    if not re.match(r"^[a-z0-9][a-z0-9_-]*$", slug):
        raise ValueError("Slug must be lowercase alphanumeric with optional - or _")


def slug_path(slug):
    return ROOT / "02_client_work" / slug


def plugin_runtime_context(slug, base_dir):
    return {
        "slug": slug,
        "base_dir": base_dir.as_posix(),
        "telemetry_log_path": (base_dir / "05_change_log" / "plugin_telemetry.jsonl").as_posix(),
    }


def _resolve_session_id():
    for key in ["CODEX_SESSION_ID", "OPENAI_SESSION_ID", "SESSION_ID"]:
        value = os.environ.get(key, "").strip()
        if value:
            return f"{key}={value}"
    return "session=unknown"


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

    memo_text = (
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
        "- Non-representational advisory only.\n"
    )
    memo_path = base_dir / "03_memo" / "Decision_Memo.md"
    memo_path.write_text(memo_text, encoding="utf-8")

    initialize_package_skeleton(base_dir, slug)
    print(f"Initialized client: {slug}")


def cmd_validate(slug, base_dir=None, plugin_manager=None, quiet=False):
    if base_dir is None:
        validate_slug(slug)
        base_dir = slug_path(slug)
    if not base_dir.is_dir():
        print(f"ERROR: Client slug not found: {slug}", file=sys.stderr)
        return 2, []

    plugin_manager = plugin_manager or PluginManager()
    context = plugin_runtime_context(slug, base_dir)
    plugin_manager.workflow_before_stage("validate", context)
    results = run_gates(
        base_dir,
        slug=slug,
        plugin_manager=plugin_manager,
        plugin_runtime_context=plugin_runtime_context,
    )
    if not quiet:
        print_results(results)

    exit_code = 0 if all(r.status for r in results) else 1
    if not quiet:
        print("VALIDATION: PASS" if exit_code == 0 else "VALIDATION: FAIL")

    plugin_manager.workflow_after_stage(
        "validate",
        {
            **context,
            "exit_code": exit_code,
            "result": "pass" if exit_code == 0 else "fail",
        },
    )
    return exit_code, results


def cmd_build_memo(slug, base_dir=None, plugin_manager=None, quiet=False):
    if base_dir is None:
        validate_slug(slug)
        base_dir = slug_path(slug)
    if not base_dir.is_dir():
        print(f"ERROR: Client slug not found: {slug}", file=sys.stderr)
        return 2

    plugin_manager = plugin_manager or PluginManager()
    context = plugin_runtime_context(slug, base_dir)
    plugin_manager.workflow_before_stage("build-memo", context)

    try:
        artifacts = build_memo_artifacts(base_dir, slug)
        write_manifest(base_dir, command_name="build-memo")
    except RuntimeError as exc:
        plugin_manager.workflow_after_stage(
            "build-memo",
            {
                **context,
                "exit_code": 1,
                "result": "fail",
                "error": str(exc),
            },
        )
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    plugin_manager.workflow_after_stage(
        "build-memo",
        {
            **context,
            "exit_code": 0,
            "result": "pass",
            "memo_pdf": artifacts["memo_pdf"],
        },
    )
    if not quiet:
        print(f"BUILD-MEMO: PASS ({artifacts['memo_pdf']})")
    return 0


def cmd_package(slug, base_dir=None, plugin_manager=None, quiet=False, skip_build=False):
    if base_dir is None:
        validate_slug(slug)
        base_dir = slug_path(slug)
    if not base_dir.is_dir():
        print(f"ERROR: Client slug not found: {slug}", file=sys.stderr)
        return 2, []

    plugin_manager = plugin_manager or PluginManager()
    context = plugin_runtime_context(slug, base_dir)
    plugin_manager.workflow_before_stage("package", context)

    if not skip_build:
        build_exit = cmd_build_memo(
            slug,
            base_dir=base_dir,
            plugin_manager=plugin_manager,
            quiet=True,
        )
        if build_exit != 0:
            plugin_manager.workflow_after_stage(
                "package",
                {
                    **context,
                    "exit_code": build_exit,
                    "result": "fail",
                    "error": "build-memo failed",
                },
            )
            return build_exit, []

    gate_report_path = base_dir / "04_package" / "gate_report.json"
    if not gate_report_path.is_file():
        write_json(
            gate_report_path,
            {
                "slug": slug,
                "generated_at": utc_now(),
                "status": "pending",
                "gates": [],
            },
        )

    write_manifest(base_dir, command_name="package")
    exit_code, results = cmd_validate(
        slug,
        base_dir=base_dir,
        plugin_manager=plugin_manager,
        quiet=True,
    )
    write_gate_report(base_dir, slug, results)

    append_runlog_event(
        base_dir,
        {
            "timestamp": utc_now(),
            "slug": slug,
            "command": "package",
            "status": "pass" if exit_code == 0 else "fail",
            "gates": [result.as_dict() for result in results],
        },
    )
    write_manifest(base_dir, command_name="package")

    if not quiet:
        print_results(results)
        print("PACKAGE: PASS" if exit_code == 0 else "PACKAGE: FAIL")

    plugin_manager.workflow_after_stage(
        "package",
        {
            **context,
            "exit_code": exit_code,
            "result": "pass" if exit_code == 0 else "fail",
        },
    )
    return exit_code, results


def _non_packaging_failures(results):
    return [result for result in results if not result.status and result.gate_id != "D"]


def cmd_run(slug, plugin_manager=None):
    validate_slug(slug)
    base_dir = slug_path(slug)
    if not base_dir.is_dir():
        raise RuntimeError(f"Client slug not found: {slug}")

    plugin_manager = plugin_manager or PluginManager()
    context = plugin_runtime_context(slug, base_dir)
    plugin_manager.workflow_before_stage("run", context)

    pre_exit, pre_results = cmd_validate(
        slug,
        base_dir=base_dir,
        plugin_manager=plugin_manager,
        quiet=True,
    )
    blocking = _non_packaging_failures(pre_results)
    if blocking:
        print_results(pre_results)
        print("RUN: BLOCKED (non-packaging gates failed before build/package)")
        plugin_manager.workflow_after_stage(
            "run",
            {
                **context,
                "exit_code": pre_exit,
                "result": "fail",
            },
        )
        sys.exit(1)

    build_exit = cmd_build_memo(
        slug,
        base_dir=base_dir,
        plugin_manager=plugin_manager,
        quiet=True,
    )
    if build_exit != 0:
        print("RUN: BLOCKED (build-memo failed)")
        plugin_manager.workflow_after_stage(
            "run",
            {
                **context,
                "exit_code": build_exit,
                "result": "fail",
            },
        )
        sys.exit(build_exit)

    exit_code, results = cmd_package(
        slug,
        base_dir=base_dir,
        plugin_manager=plugin_manager,
        quiet=True,
        skip_build=True,
    )

    print_results(results)
    if exit_code != 0:
        print("RUN: BLOCKED (package stage requires all gates to pass)")
        plugin_manager.workflow_after_stage(
            "run",
            {
                **context,
                "exit_code": exit_code,
                "result": "fail",
            },
        )
        sys.exit(exit_code)

    engine = OrchestrationEngine(base_dir)
    try:
        engine.require_package_allowed(results)
    except OrchestrationError as exc:
        print(f"ERROR: Package stage blocked by orchestration: {exc}", file=sys.stderr)
        plugin_manager.workflow_after_stage(
            "run",
            {
                **context,
                "exit_code": 1,
                "result": "fail",
                "error": str(exc),
            },
        )
        sys.exit(1)

    run_timestamp = datetime.now(timezone.utc)
    run_dir = ROOT / "runs" / run_timestamp.strftime(f"%Y%m%d_{slug}_%H%M%SZ")
    run_dir.mkdir(parents=True, exist_ok=True)

    append_runlog_event(
        base_dir,
        {
            "timestamp": utc_now(),
            "slug": slug,
            "command": "run",
            "status": "pass",
            "run_dir": run_dir.as_posix(),
        },
    )
    write_manifest(base_dir, command_name="run")

    manifest_src = base_dir / "04_package" / "manifest.json"
    gate_report_src = base_dir / "04_package" / "gate_report.json"
    runlog_src = base_dir / "04_package" / "runlog.jsonl"

    manifest_dst = run_dir / "manifest.json"
    gate_report_dst = run_dir / "gate_report.json"
    runlog_dst = run_dir / "runlog.jsonl"

    shutil.copy2(manifest_src, manifest_dst)
    shutil.copy2(gate_report_src, gate_report_dst)
    shutil.copy2(runlog_src, runlog_dst)

    generated_at = run_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
    build_log_path = run_dir / "build_log.txt"
    build_log_path.write_text(f"{generated_at} pass\n", encoding="utf-8")

    session_pointer_path = run_dir / "codex_session_pointer.txt"
    session_pointer_path.write_text(
        "\n".join(
            [
                _resolve_session_id(),
                f"generated_at={generated_at}",
                f"slug={slug}",
                f"package_runlog={(base_dir / '04_package' / 'runlog.jsonl').resolve().as_posix()}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    record = {
        "slug": slug,
        "generated_at": generated_at,
        "status": "pass",
        "manifest": manifest_dst.resolve().as_posix(),
        "gate_report": gate_report_dst.resolve().as_posix(),
        "runlog": runlog_dst.resolve().as_posix(),
        "build_log": build_log_path.resolve().as_posix(),
        "codex_session_pointer": session_pointer_path.resolve().as_posix(),
        "plugins": plugin_manager.active_plugins(),
    }
    record_path = run_dir / "run_record.json"
    write_json(record_path, record)

    plugin_manager.workflow_after_stage(
        "run",
        {
            **context,
            "run_dir": run_dir.as_posix(),
            "exit_code": 0,
            "result": "pass",
        },
    )
    print(f"RUN: PASS ({run_dir.as_posix()})")


def parse_eval_suite(path):
    if not path.is_file():
        raise RuntimeError(f"Regression suite not found: {path}")
    lines = path.read_text(encoding="utf-8").splitlines()
    in_cases = False
    current = None
    cases = []
    for raw in lines:
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if not in_cases:
            if stripped == "cases:":
                in_cases = True
            continue
        if raw.lstrip().startswith("- "):
            if current is not None:
                cases.append(current)
            current = {"path": "", "expect": "pass", "gate": None}
            value = raw.lstrip()[2:].strip()
            if not value:
                continue
            if ":" in value:
                key, item_value = value.split(":", 1)
                key = key.strip()
                item_value = item_value.strip()
                if key == "path":
                    current["path"] = item_value
                elif key == "expect":
                    current["expect"] = item_value.lower()
                elif key == "gate":
                    current["gate"] = item_value.upper()
            else:
                current["path"] = value
            continue
        if current is None or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        key = key.strip()
        value = value.strip()
        if key == "path":
            current["path"] = value
        elif key == "expect":
            current["expect"] = value.lower()
        elif key == "gate":
            current["gate"] = value.upper()
    if current is not None:
        cases.append(current)

    normalized = []
    for idx, case in enumerate(cases, start=1):
        case_path = str(case.get("path", "")).strip()
        if not case_path:
            raise RuntimeError(f"Case #{idx} is missing path in regression_suite.yml")
        expect = str(case.get("expect", "pass")).strip().lower()
        if expect not in {"pass", "fail"}:
            raise RuntimeError(f"Case {case_path} has invalid expect value: {expect}")
        gate = case.get("gate")
        gate = str(gate).strip().upper() if gate else None
        normalized.append({"path": case_path, "expect": expect, "gate": gate})
    return normalized


def first_failed_gate(results):
    for result in results:
        if not result.status:
            return result.gate_id
    return None


def cmd_eval(plugin_manager=None, include_negative=False):
    plugin_manager = plugin_manager or PluginManager()
    suite_path = ROOT / "04_evals" / "regression_suite.yml"
    cases = parse_eval_suite(suite_path)

    selected_cases = []
    for case in cases:
        if case["expect"] == "fail" and not include_negative:
            continue
        selected_cases.append(case)
    if not selected_cases:
        raise RuntimeError("No cases selected from regression_suite.yml")

    plugin_manager.workflow_before_stage(
        "eval",
        {
            "suite_path": suite_path.as_posix(),
            "include_negative": include_negative,
        },
    )

    failures = 0
    expected_failures = 0
    for case in selected_cases:
        case_path = case["path"]
        base_dir = ROOT / case_path
        slug = base_dir.name
        expect = case["expect"]
        expected_gate = case["gate"]
        context = plugin_runtime_context(slug, base_dir)
        plugin_manager.eval_before_case(case_path, slug, context)

        if not base_dir.is_dir():
            print(f"EVAL CASE FAIL: {case_path} (missing directory)")
            failures += 1
            plugin_manager.eval_after_case(case_path, slug, 1, {**context, "status": "missing"})
            continue

        exit_code, results = cmd_validate(
            slug,
            base_dir=base_dir,
            plugin_manager=plugin_manager,
            quiet=True,
        )
        failed_gate = first_failed_gate(results)
        status = "pass" if exit_code == 0 else "fail"
        plugin_manager.eval_after_case(
            case_path,
            slug,
            exit_code,
            {**context, "status": status, "failed_gate": failed_gate or ""},
        )

        if expect == "pass":
            if exit_code == 0:
                print(f"EVAL CASE PASS: {case_path}")
            else:
                print(
                    f"EVAL CASE FAIL: {case_path} expected pass but failed at gate {failed_gate}"
                )
                failures += 1
            continue

        gate_ok = expected_gate is None or expected_gate == failed_gate
        if exit_code != 0 and gate_ok:
            expected_failures += 1
            gate_detail = f" gate {failed_gate}" if failed_gate else ""
            print(f"EVAL CASE PASS: {case_path} (expected{gate_detail})")
            continue

        if exit_code == 0:
            print(f"EVAL CASE FAIL: {case_path} expected failure but passed")
        else:
            print(
                f"EVAL CASE FAIL: {case_path} expected gate {expected_gate} but failed at {failed_gate}"
            )
        failures += 1

    if failures:
        print(f"EVAL: FAIL ({failures} case(s))")
        plugin_manager.workflow_after_stage(
            "eval",
            {
                "suite_path": suite_path.as_posix(),
                "include_negative": include_negative,
                "failures": failures,
                "expected_failures": expected_failures,
                "result": "fail",
            },
        )
        sys.exit(1)

    summary = (
        f"EVAL: PASS ({len(selected_cases)} case(s), {expected_failures} expected failures)"
        if include_negative
        else f"EVAL: PASS ({len(selected_cases)} case(s))"
    )
    print(summary)
    plugin_manager.workflow_after_stage(
        "eval",
        {
            "suite_path": suite_path.as_posix(),
            "include_negative": include_negative,
            "failures": 0,
            "expected_failures": expected_failures,
            "result": "pass",
        },
    )


def parse_enabled_plugins(value):
    if value is None:
        return None
    parts = [part.strip() for part in value.split(",")]
    return [part for part in parts if part]


def build_plugin_manager(enabled_plugins):
    allowlist_path = ROOT / "00_governance" / "PLUGIN_ALLOWLIST.json"
    return PluginManager.from_allowlist(
        allowlist_path=allowlist_path,
        enabled_plugin_ids=enabled_plugins,
    )


def build_parser():
    parser = argparse.ArgumentParser(prog="tesgi", description="TESGI Advisory OS tooling")
    sub = parser.add_subparsers(dest="command", required=True)

    init_client = sub.add_parser("init-client", help="Initialize client workspace")
    init_client.add_argument("slug")

    validate = sub.add_parser("validate", help="Validate client workspace")
    validate.add_argument("slug")
    validate.add_argument(
        "--plugins",
        help="Comma-separated allowlisted plugin ids, or 'all'",
    )

    build_memo = sub.add_parser("build-memo", help="Build memo artifacts for a client workspace")
    build_memo.add_argument("slug")
    build_memo.add_argument(
        "--plugins",
        help="Comma-separated allowlisted plugin ids, or 'all'",
    )

    package = sub.add_parser("package", help="Package deliverables and validate all gates")
    package.add_argument("slug")
    package.add_argument(
        "--plugins",
        help="Comma-separated allowlisted plugin ids, or 'all'",
    )

    run = sub.add_parser("run", help="Run validation, build-memo, and package")
    run.add_argument("slug")
    run.add_argument(
        "--plugins",
        help="Comma-separated allowlisted plugin ids, or 'all'",
    )

    eval_cmd = sub.add_parser("eval", help="Run evaluation suite")
    eval_cmd.add_argument(
        "--plugins",
        help="Comma-separated allowlisted plugin ids, or 'all'",
    )
    eval_cmd.add_argument(
        "--include-negative",
        action="store_true",
        help="Include cases marked expect: fail in regression_suite.yml",
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "init-client":
        cmd_init_client(args.slug)
        return

    plugin_manager = None
    if args.command in {"validate", "build-memo", "package", "run", "eval"}:
        enabled_plugins = parse_enabled_plugins(getattr(args, "plugins", None))
        try:
            plugin_manager = build_plugin_manager(enabled_plugins)
        except PluginConfigError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            sys.exit(2)

    if args.command == "validate":
        exit_code, _ = cmd_validate(args.slug, plugin_manager=plugin_manager)
        sys.exit(exit_code)

    if args.command == "build-memo":
        exit_code = cmd_build_memo(args.slug, plugin_manager=plugin_manager)
        sys.exit(exit_code)

    if args.command == "package":
        exit_code, _ = cmd_package(args.slug, plugin_manager=plugin_manager)
        sys.exit(exit_code)

    if args.command == "run":
        cmd_run(args.slug, plugin_manager=plugin_manager)
        return

    if args.command == "eval":
        cmd_eval(
            plugin_manager=plugin_manager,
            include_negative=getattr(args, "include_negative", False),
        )
        return


if __name__ == "__main__":
    main()
