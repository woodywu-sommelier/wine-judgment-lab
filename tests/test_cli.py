import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class CliTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, "-m", "wine_judgment_lab", *args], text=True, capture_output=True)

    def test_demo_exports_labeled_synthetic_results_and_hf_dataset(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "demo"
            result = self.run_cli("demo", "--out", str(out))
            self.assertEqual(result.returncode, 0, result.stderr)
            summary = json.loads((out / "summary.json").read_text())
            self.assertEqual(summary["provider"], "simulated")
            self.assertEqual(summary["data_kind"], "synthetic")
            self.assertEqual(summary["estate_count"], 2)
            data = (out / "huggingface" / "data" / "trials.jsonl").read_text().splitlines()
            self.assertEqual(len(data), 6)
            self.assertTrue(all(json.loads(line)["synthetic"] for line in data))
            self.assertTrue((out / "huggingface" / "README.md").is_file())
            self.assertEqual(json.loads((out / "manifest.json").read_text())["api_calls"], 0)

    def test_demo_refuses_overwrite_and_preserves_existing_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "existing"; out.mkdir()
            marker = out / "owner.txt"; marker.write_text("keep")
            result = self.run_cli("demo", "--out", str(out))
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(marker.read_text(), "keep")
            self.assertEqual(list(out.iterdir()), [marker])

    def test_invalid_analysis_does_not_create_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.jsonl"; bad.write_text('{"wrong":"schema"}\n')
            output = Path(tmp) / "summary.json"
            result = self.run_cli("analyze", "--trials", str(bad), "--judgments", str(bad), "--out", str(output))
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(output.exists())

    def test_prepare_rejects_duplicate_json_keys_without_partial_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.json"; bad.write_text('{"rows":[],"rows":[]}')
            output = Path(tmp) / "prepared"
            result = self.run_cli("prepare", "--dossiers", str(bad), "--rubric", str(bad), "--out", str(output))
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
