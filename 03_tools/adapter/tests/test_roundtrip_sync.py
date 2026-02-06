import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CLAUDE_TO_TESGI = ROOT / "03_tools" / "adapter" / "claude_to_tesgi.py"
TESGI_TO_CLAUDE = ROOT / "03_tools" / "adapter" / "tesgi_to_claude.py"


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def run_script(script: Path, args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(script), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


class AdapterSyncDeleteTests(unittest.TestCase):
    def test_claude_to_tesgi_sync_delete_prunes_only_managed_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            claude_root = tmp_path / "claude" / "clients"
            tesgi_root = tmp_path / "tesgi" / "02_client_work"

            client_dir = claude_root / "alpha-client"
            write_text(client_dir / "intake.md", "intake")
            write_text(client_dir / "analysis" / "true.md", "true")
            write_text(client_dir / "analysis" / "north.md", "north")
            write_text(client_dir / "analysis" / "aligned.md", "aligned")
            write_text(client_dir / "analysis" / "esg.md", "esg")
            write_text(client_dir / "memo.md", "memo")
            write_text(client_dir / "sources" / "source-a.txt", "a")

            first = run_script(
                CLAUDE_TO_TESGI,
                [
                    "alpha-client",
                    "--claude-root",
                    str(claude_root),
                    "--tesgi-root",
                    str(tesgi_root),
                ],
            )
            self.assertEqual(first.returncode, 0, first.stderr)
            payload = json.loads(first.stdout)
            slug = payload["slug"]
            dst = tesgi_root / slug

            write_text(dst / "05_change_log" / "keep.txt", "keep")
            write_text(dst / "01_sources" / "stale.txt", "stale")
            write_text(dst / "02_analysis" / "esg.md", "stale esg")

            (client_dir / "analysis" / "esg.md").unlink()
            (client_dir / "sources" / "source-a.txt").unlink()

            second = run_script(
                CLAUDE_TO_TESGI,
                [
                    "alpha-client",
                    "--claude-root",
                    str(claude_root),
                    "--tesgi-root",
                    str(tesgi_root),
                    "--force",
                    "--sync-delete",
                ],
            )
            self.assertEqual(second.returncode, 0, second.stderr)
            second_payload = json.loads(second.stdout)

            self.assertTrue(second_payload["pruned"]["esg"])
            self.assertGreaterEqual(second_payload["sources_files_pruned"], 1)
            self.assertFalse((dst / "02_analysis" / "esg.md").exists())
            self.assertFalse((dst / "01_sources" / "stale.txt").exists())
            self.assertTrue((dst / "05_change_log" / "keep.txt").exists())

    def test_tesgi_to_claude_sync_delete_prunes_only_managed_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            tesgi_root = tmp_path / "tesgi" / "02_client_work"
            claude_root = tmp_path / "claude" / "clients"

            slug = "demo"
            src = tesgi_root / slug
            write_text(src / "00_intake" / "intake.md", "intake")
            write_text(
                src / "00_intake" / "intake_ack.json",
                json.dumps({"source_client_id": "alpha-client"}),
            )
            write_text(src / "02_analysis" / "true.md", "true")
            write_text(src / "02_analysis" / "north.md", "north")
            write_text(src / "02_analysis" / "aligned.md", "aligned")
            write_text(src / "02_analysis" / "esg.md", "esg")
            write_text(src / "03_memo" / "Decision_Memo.md", "memo")
            write_text(src / "01_sources" / "source-a.txt", "a")

            first = run_script(
                TESGI_TO_CLAUDE,
                [
                    slug,
                    "--tesgi-root",
                    str(tesgi_root),
                    "--claude-root",
                    str(claude_root),
                ],
            )
            self.assertEqual(first.returncode, 0, first.stderr)
            payload = json.loads(first.stdout)
            dst = claude_root / payload["client_id"]

            write_text(dst / "notes_keep.txt", "keep")
            write_text(dst / "analysis" / "esg.md", "stale esg")
            write_text(dst / "sources" / "stale.txt", "stale")

            (src / "02_analysis" / "esg.md").unlink()
            (src / "01_sources" / "source-a.txt").unlink()

            second = run_script(
                TESGI_TO_CLAUDE,
                [
                    slug,
                    "--tesgi-root",
                    str(tesgi_root),
                    "--claude-root",
                    str(claude_root),
                    "--force",
                    "--sync-delete",
                ],
            )
            self.assertEqual(second.returncode, 0, second.stderr)
            second_payload = json.loads(second.stdout)

            self.assertTrue(second_payload["pruned"]["esg"])
            self.assertGreaterEqual(second_payload["sources_files_pruned"], 1)
            self.assertFalse((dst / "analysis" / "esg.md").exists())
            self.assertFalse((dst / "sources" / "stale.txt").exists())
            self.assertTrue((dst / "notes_keep.txt").exists())

    def test_sync_delete_requires_force(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            claude_root = tmp_path / "claude" / "clients"
            tesgi_root = tmp_path / "tesgi" / "02_client_work"
            client_dir = claude_root / "alpha-client"
            write_text(client_dir / "intake.md", "intake")

            result = run_script(
                CLAUDE_TO_TESGI,
                [
                    "alpha-client",
                    "--claude-root",
                    str(claude_root),
                    "--tesgi-root",
                    str(tesgi_root),
                    "--sync-delete",
                ],
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("--sync-delete requires --force", result.stderr)


if __name__ == "__main__":
    unittest.main()
