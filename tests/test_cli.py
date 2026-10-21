import json
import hashlib
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
            self.assertEqual(summary["estate_count"], 5)
            data = (out / "huggingface" / "data" / "trials.jsonl").read_text().splitlines()
            self.assertEqual(len(data), 6)
            self.assertEqual(hashlib.sha256((out / "huggingface" / "data" / "trials.jsonl").read_bytes()).hexdigest(),
                             "8db5a7b7ddb76d1f0e2d5f7e278c57aed70aeceedaf4345b605b9049d3d6d125")
            revised = [json.loads(line) for line in (out / "huggingface" / "data" / "v0.2" / "trials.jsonl").read_text().splitlines()]
            self.assertEqual(len(revised), 20)
            self.assertEqual(hashlib.sha256((out / "huggingface" / "data" / "v0.2" / "trials.jsonl").read_bytes()).hexdigest(),
                             "7ca5825149fbd9620f2bafc92021e5dd16674432c8c24f51ea34a934e1af4ab8")
            revised = [json.loads(line) for line in (out / "huggingface" / "data" / "v0.3" / "trials.jsonl").read_text().splitlines()]
            self.assertEqual(len(revised), 20)
            for row in revised:
                self.assertNotIn("verification", row["state_json"])
                self.assertNotIn("verification", json.dumps(row))
                for key in ("analyst_assessments", "completeness", "expected_label", "adjudicated_by", "adjudicated_at", "agreement"):
                    self.assertNotIn(key, json.dumps(row))
            trial_text = (out / "trials.jsonl").read_text()
            for key in ("analyst_assessments", "completeness", "expected_label", "adjudicated_at", "adjudicated_by", "agreement"):
                self.assertNotIn(key, trial_text)
            private = out / "analyst_records.json"
            records = json.loads(private.read_text())
            self.assertEqual(records[0]["evidence"][0]["verification"], "independent")
            self.assertEqual(private.stat().st_mode & 0o777, 0o600)
            self.assertIsNone(records[0]["analyst_assessments"][0]["expected_label"])
            self.assertEqual(records[2]["analyst_assessments"][0]["completeness"], "partial")
            self.assertEqual(records[4]["analyst_assessments"][0]["completeness"], "conflicting")
            self.assertEqual(len(records[4]["evidence"]), 2)
            self.assertEqual(len({e["source_id"] for e in records[4]["evidence"]}), 2)
            self.assertEqual((out / "analyst_review.json").stat().st_mode & 0o777, 0o600)
            trials = {row["trial_id"]: row for row in map(json.loads, trial_text.splitlines())}
            judgments = list(map(json.loads, (out / "simulated_judgments.jsonl").read_text().splitlines()))
            partial = [j for j in judgments if trials[j["trial_id"]]["estate_id"] == "fiction-04"
                       and j["criterion_id"] == "vintage_consistency"]
            self.assertEqual(len(partial), 8)
            self.assertEqual({j["label"] for j in partial}, {"insufficient_evidence"})
            self.assertFalse(list((out / "huggingface").rglob("*analyst*")))
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

    def test_reference_check_rejects_pending_without_output_then_accepts_dated_adjudication(self):
        from test_experiment import dossiers, rubric
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); data = root / "dossiers.json"; questions = root / "rubric.json"; out = root / "readiness.json"
            rows = dossiers()
            data.write_text(json.dumps(rows)); questions.write_text(json.dumps(rubric()))
            args = ("check-reference", "--dossiers", str(data), "--rubric", str(questions),
                    "--first-run-at", "2026-10-21T12:00:00Z", "--out", str(out))
            result = self.run_cli(*args)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(out.exists())
            rows[0]["analyst_assessments"][0].update(expected_label="supported",
                adjudicated_by=["Fictional reviewer"], adjudicated_at="2026-10-20", agreement="single_reviewer")
            data.write_text(json.dumps(rows))
            result = self.run_cli(*args)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(out.read_text())["assessment_count"], 1)
            self.assertEqual(out.stat().st_mode & 0o777, 0o600)

    def test_manifest_separates_judge_payload_and_private_record_hashes(self):
        from test_analyst import adjudicated
        from test_experiment import rubric
        from wine_judgment_lab.__main__ import _prepare
        import copy
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); original = adjudicated()
            changed = copy.deepcopy(original)
            changed[0]["analyst_assessments"][0].update(completeness="conflicting", expected_label="insufficient_evidence")
            _prepare(original, rubric(), 19, root / "first")
            _prepare(changed, rubric(), 19, root / "second")
            first = json.loads((root / "first/manifest.json").read_text())
            second = json.loads((root / "second/manifest.json").read_text())
            self.assertNotIn("dossiers_sha256", first)
            self.assertEqual(first["judge_dossiers_sha256"], second["judge_dossiers_sha256"])
            self.assertNotEqual(first["analyst_records_sha256"], second["analyst_records_sha256"])
            self.assertEqual(first["trials_sha256"], second["trials_sha256"])


if __name__ == "__main__":
    unittest.main()
