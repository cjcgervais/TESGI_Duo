import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path

from tesgi.orchestration.contracts import STAGE_CONTRACTS
from tesgi.orchestration.engine import OrchestrationEngine, OrchestrationError


@dataclass
class DummyGate:
    gate_id: str
    status: bool


class ForcedPackageStageEngine(OrchestrationEngine):
    def infer_stage(self, passed_gates=()):
        return "package_passed"


class OrchestrationContractTests(unittest.TestCase):
    def test_package_and_eval_contracts_require_all_core_gates(self) -> None:
        expected = ("O", "A", "B", "C", "D", "E")
        self.assertEqual(STAGE_CONTRACTS["package_passed"].required_gates, expected)
        self.assertEqual(STAGE_CONTRACTS["eval_passed"].required_gates, expected)

    def test_stage_schema_is_enforced_during_evaluation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base_dir = Path(tmp)
            engine = ForcedPackageStageEngine(base_dir)
            status = engine.evaluate(gate_results=[DummyGate("A", True)])
            self.assertFalse(status.valid)
            self.assertTrue(status.schema_errors)

    def test_require_package_allowed_blocks_missing_gate_even_with_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base_dir = Path(tmp)
            for rel in STAGE_CONTRACTS["package_passed"].required_files:
                path = base_dir / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                if rel.endswith("Decision_Memo.md"):
                    path.write_text(
                        "# Decision Memo\n\n"
                        "## Decision State\n"
                        "- [x] Proceed\n\n"
                        "## What This Memo Does Not Say\n"
                        "- Non-representational advisory only.\n",
                        encoding="utf-8",
                    )
                else:
                    path.write_text("fixture\n", encoding="utf-8")

            gates_without_o = [
                DummyGate("A", True),
                DummyGate("B", True),
                DummyGate("C", True),
                DummyGate("D", True),
                DummyGate("E", True),
            ]

            engine = OrchestrationEngine(base_dir)
            with self.assertRaises(OrchestrationError) as ctx:
                engine.require_package_allowed(gates_without_o)
            self.assertIn("O", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
