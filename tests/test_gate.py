import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

EXAMPLE = Path(__file__).resolve().parents[1] / "wine_judgment_lab" / "data" / "gate-example.jsonl"


def row(entity, condition, repeat, score, sufficiency, **extra):
    return {"entity_id": entity, "condition": condition, "repeat_id": repeat, "run_id": "r",
            "score": score, "sufficiency": sufficiency, "provider": "simulated",
            "model": "synthetic-demo", "synthetic": True} | extra


def design():
    # Named sufficiency per entity, masked = named - 0.05 (entity C unchanged).
    rows = []
    for entity, score, named in (("A", 3.0, 0.72), ("B", 2.5, 0.68), ("C", 2.0, 0.90), ("D", 1.0, 0.40)):
        masked = named if entity == "C" else named - 0.05
        for repeat in (0, 1):
            rows.append(row(entity, "named", repeat, score, named))
            rows.append(row(entity, "masked", repeat, score - 0.1, masked))
    return rows


class GateTests(unittest.TestCase):
    def audit(self, rows=None, **kwargs):
        from wine_judgment_lab.gate import gate_audit
        return gate_audit(design() if rows is None else rows, cutoffs=(0.65, 0.70), **kwargs)

    def test_qualification_flips_and_near_cutoff_are_hand_checked(self):
        gates = self.audit()["all"]["comparisons"]["named_vs_masked"]["qualification_by_cutoff"]
        # 0.70: named A, C qualify; masked only C (A 0.67). B is 0.68 named, 0.63 masked.
        self.assertEqual(gates["0.70"], {"only_named": 1, "only_masked": 0, "both": 1, "near_cutoff_in_named": 2})
        # 0.65: named A, B, C; masked A (0.67), C. B drops. Only B (0.68) is within 0.03 of 0.65.
        self.assertEqual(gates["0.65"], {"only_named": 1, "only_masked": 0, "both": 2, "near_cutoff_in_named": 1})

    def test_shift_counts_scores_and_leaders(self):
        result = self.audit()["all"]
        shift = result["comparisons"]["named_vs_masked"]["sufficiency_shift"]
        self.assertEqual((shift["down"], shift["up"], shift["unchanged"]), (3, 0, 1))
        self.assertEqual(shift["median"], -0.05)
        self.assertEqual(shift["sign_test_two_sided_p"], 0.25)  # 3 of 3 down: 2 * 1/8
        score = result["comparisons"]["named_vs_masked"]["score"]
        self.assertEqual(score["spearman_all_entities"], 1.0)
        self.assertEqual(score["median_absolute_shift"], 0.1)
        named = result["conditions"]["named"]
        self.assertEqual(named["leader_without_cutoff"], "A")
        self.assertEqual(named["by_cutoff"]["0.70"]["leader"], "A")
        self.assertEqual(result["conditions"]["masked"]["by_cutoff"]["0.70"]["leader"], "C")

    def test_repeat_noise_is_reported_for_the_gate(self):
        rows = design()
        for r in rows:
            if r["entity_id"] == "A" and r["condition"] == "named" and r["repeat_id"] == 1:
                r["sufficiency"] = 0.69  # crosses 0.70 between repeats
        named = self.audit(rows)["all"]["conditions"]["named"]
        self.assertEqual(named["by_cutoff"]["0.70"]["unstable_across_repeats"], 1)
        self.assertEqual(named["by_cutoff"]["0.65"]["unstable_across_repeats"], 0)
        self.assertEqual(named["median_repeat_sufficiency_difference"], 0.0)

    def test_median_on_the_cutoff_qualifies_despite_float_error(self):
        rows = [row("A", c, rep, 1.0, s) for c in ("named", "masked") for rep, s in ((0, 0.71), (1, 0.69))]
        rows += [row(e, c, rep, 1.0, 0.5) for e in ("B", "C") for c in ("named", "masked") for rep in (0, 1)]
        result = self.audit(rows)["all"]["conditions"]["named"]["by_cutoff"]["0.70"]
        self.assertEqual(result["qualified"], 1)

    def test_clean_subset_and_external_rank_orientation(self):
        ranks = {"A": 1, "B": 2, "C": 3, "D": 4}  # 1 = best, same order as named scores
        result = self.audit(leaks={"A": True}, external_ranks=ranks)
        self.assertEqual(result["all"]["conditions"]["named"]["spearman_with_external_ranks"], 1.0)
        clean = result["clean"]
        self.assertEqual(clean["entity_count"], 3)
        self.assertEqual(clean["comparisons"]["named_vs_masked"]["qualification_by_cutoff"]["0.70"]["only_named"], 0)
        self.assertIsNone(self.audit()["clean"])

    def test_single_repeat_needs_explicit_exploratory_mode(self):
        rows = [r for r in design() if r["repeat_id"] == 0]
        with self.assertRaisesRegex(ValueError, "At least 2 repeats"):
            self.audit(rows)
        result = self.audit(rows, min_repeats=1)
        self.assertTrue(result["exploratory_single_repeat"])

    def test_invalid_designs_are_rejected(self):
        from wine_judgment_lab.gate import gate_audit
        cases = [
            design()[1:],                                            # missing cell
            design() + [design()[0]],                                # duplicate
            [dict(r, sufficiency=1.2) for r in design()],            # out of range
            [dict(r, score=float("nan")) for r in design()],         # nonfinite
            [dict(r, model="other") if i == 0 else r for i, r in enumerate(design())],  # mixed judges
            [dict(r, synthetic="yes") for r in design()],            # implicit flag
        ]
        for rows in cases:
            with self.subTest(rows=len(rows)), self.assertRaises(ValueError):
                gate_audit(rows)
        with self.assertRaises(ValueError):
            gate_audit(design(), reference="anonymous")
        with self.assertRaises(ValueError):
            gate_audit(design(), cutoffs=(0, 0.7))
        with self.assertRaises(ValueError):
            gate_audit(design(), leaks={"Z": True})

    def test_spearman_handles_ties_and_degenerate_input(self):
        from wine_judgment_lab.gate import spearman
        self.assertAlmostEqual(spearman([1, 2, 2, 3], [1, 2, 3, 4]), 0.9487, places=4)
        self.assertIsNone(spearman([1, 1, 1], [1, 2, 3]))
        self.assertIsNone(spearman([1, 2], [1, 2]))

    def test_cli_runs_example_without_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "gate.json"
            args = [sys.executable, "-m", "wine_judgment_lab", "gate", "--judgments", str(EXAMPLE), "--out", str(out)]
            result = subprocess.run(args, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(out.read_text())
            self.assertEqual(data["data_kind"], "synthetic")
            self.assertEqual(data["all"]["comparisons"]["named_vs_masked"]["qualification_by_cutoff"]["0.70"]["only_named"], 2)
            self.assertNotEqual(subprocess.run(args, text=True, capture_output=True).returncode, 0)


if __name__ == "__main__":
    unittest.main()
