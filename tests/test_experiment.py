import copy
import unittest


def dossiers():
    return [{
        "estate_id": "fiction-01", "producer_name": "Domaine Example A",
        "swap_name": "Domaine Example B", "region": "Burgundy",
        "synthetic": True, "identity_leakage": False, "swap_plausible": True,
        "evidence": [{"criterion_id": "farming", "observation": "An independent record supports the stated farming claim.",
                      "verification": "independent", "source_id": "s1"}],
        "sources": [{"source_id": "s1", "url": "https://example.org/fiction-01", "rights": "original_synthetic"}],
    }]


def rubric():
    return {"version": "0.1", "questions": [{"criterion_id": "farming", "instructions": "Is the farming claim supported?",
        "labels": {"supported": "Evidence supports it", "contradicted": "Evidence contradicts it",
                   "insufficient_evidence": "Evidence is insufficient"}}]}


def judgments(trials):
    return [{"trial_id": t["trial_id"], "trial_hash": t["trial_hash"], "criterion_id": "farming",
             "label": "supported", "provider": "simulated", "model": "synthetic-demo",
             "run_id": "demo", "repeat_id": 0, "created_at": "2026-10-19T00:00:00Z"} for t in trials]


class ExperimentTests(unittest.TestCase):
    def test_identity_changes_preserve_evidence_and_remove_source_identifiers(self):
        from wine_judgment_lab.experiment import build_trials
        trials = build_trials(dossiers(), rubric(), seed=19)
        self.assertEqual(len(trials), 3)
        states = {t["condition"]: t["state"] for t in trials}
        self.assertEqual(states["named"]["producer_identity"], "Domaine Example A")
        self.assertEqual(states["anonymous"]["producer_identity"], "Identity withheld")
        self.assertEqual(states["swapped"]["producer_identity"], "Domaine Example B")
        self.assertEqual(states["named"]["observations"], states["anonymous"]["observations"])
        self.assertEqual(states["named"]["observations"], states["swapped"]["observations"])
        self.assertNotIn("source_id", states["anonymous"]["observations"][0])
        self.assertNotIn("sources", states["anonymous"])
        self.assertEqual(len({t["evidence_hash"] for t in trials}), 1)

    def test_trial_order_is_reproducible_and_independent_of_input_order(self):
        from wine_judgment_lab.experiment import build_trials
        rows = dossiers()
        second = copy.deepcopy(rows[0]); second.update(estate_id="fiction-02", producer_name="C", swap_name="D")
        rows.append(second)
        self.assertEqual(build_trials(rows, rubric(), seed=19), build_trials(list(reversed(rows)), rubric(), seed=19))

    def test_missing_evidence_stays_empty_and_is_not_an_adverse_verdict(self):
        from wine_judgment_lab.experiment import build_trials
        rows = dossiers(); rows[0]["evidence"] = []; rows[0]["sources"] = []
        self.assertTrue(all(t["state"]["observations"] == [] for t in build_trials(rows, rubric(), seed=19)))

    def test_invalid_or_duplicate_dossiers_are_rejected(self):
        from wine_judgment_lab.experiment import build_trials
        for field in ("identity_leakage", "swap_plausible", "sources"):
            rows = dossiers(); del rows[0][field]
            with self.subTest(field=field), self.assertRaises(ValueError):
                build_trials(rows, rubric(), seed=19)
        with self.assertRaises(ValueError):
            build_trials(dossiers() * 2, rubric(), seed=19)

    def test_unknown_evidence_source_is_rejected(self):
        from wine_judgment_lab.experiment import build_trials
        rows = dossiers(); rows[0]["evidence"][0]["source_id"] = "missing"
        with self.assertRaises(ValueError):
            build_trials(rows, rubric(), seed=19)

    def test_analysis_measures_label_changes_without_assigning_quality_scores(self):
        from wine_judgment_lab.experiment import build_trials, analyze
        trials = build_trials(dossiers(), rubric(), seed=19)
        result_rows = judgments(trials)
        for row in result_rows:
            if next(t for t in trials if t["trial_id"] == row["trial_id"])["condition"] == "anonymous":
                row["label"] = "insufficient_evidence"
        result = analyze(trials, result_rows)
        metric = result["criteria"]["farming"]
        self.assertEqual(metric["named_anonymous_disagreement_rate"], 1.0)
        self.assertEqual(metric["swapped_named_disagreement_rate"], 0.0)
        self.assertEqual(metric["paired_observations"], 1)
        self.assertEqual(result["data_kind"], "synthetic")

    def test_analysis_rejects_stale_hash_duplicate_and_incomplete_results(self):
        from wine_judgment_lab.experiment import build_trials, analyze
        trials = build_trials(dossiers(), rubric(), seed=19)
        invalid = judgments(trials); invalid[0]["trial_hash"] = "bad"
        for rows in (invalid, judgments(trials) + [judgments(trials)[0]], judgments(trials)[:-1]):
            with self.assertRaises(ValueError):
                analyze(trials, rows)

    def test_analysis_rejects_edited_trial_even_with_original_judgment_hash(self):
        from wine_judgment_lab.experiment import build_trials, analyze
        trials = build_trials(dossiers(), rubric(), seed=19)
        result_rows = judgments(trials)
        trials[0]["state"]["observations"][0]["text"] = "tampered"
        with self.assertRaises(ValueError):
            analyze(trials, result_rows)

    def test_analysis_separates_identity_leakage_and_implausible_swaps(self):
        from wine_judgment_lab.experiment import build_trials, analyze
        rows = dossiers(); rows[0]["identity_leakage"] = True; rows[0]["swap_plausible"] = False
        trials = build_trials(rows, rubric(), seed=19)
        metric = analyze(trials, judgments(trials))["criteria"]["farming"]
        self.assertEqual(metric["clean_paired_observations"], 0)
        self.assertIsNone(metric["clean_named_anonymous_disagreement_rate"])
        self.assertIsNone(metric["swapped_named_disagreement_rate"])

    def test_analysis_rejects_variants_with_different_evidence_even_when_rehashed(self):
        from wine_judgment_lab.experiment import build_trials, analyze, digest
        trials = build_trials(dossiers(), rubric(), seed=19)
        trials[0]["state"]["observations"][0]["text"] = "different evidence"
        trials[0]["evidence_hash"] = digest(trials[0]["state"]["observations"])
        trials[0]["trial_hash"] = digest({k: v for k, v in trials[0].items() if k != "trial_hash"})
        with self.assertRaises(ValueError):
            analyze(trials, judgments(trials))

    def test_analysis_rejects_multiple_trials_for_one_estate_condition(self):
        from wine_judgment_lab.experiment import build_trials, analyze, digest
        trials = build_trials(dossiers(), rubric(), seed=19)
        extra = copy.deepcopy(trials[0]); extra["trial_id"] = "extra"
        extra["trial_hash"] = digest({k: v for k, v in extra.items() if k != "trial_hash"})
        trials.append(extra)
        with self.assertRaises(ValueError):
            analyze(trials, judgments(trials))


if __name__ == "__main__":
    unittest.main()
