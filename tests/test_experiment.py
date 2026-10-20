import copy
import unittest


def dossiers():
    return [{
        "estate_id": "fiction-01", "producer_name": "Domaine Example A",
        "swap_name": "Domaine Example B", "neutral_name": "Domaine A", "region": "Burgundy",
        "synthetic": True, "identity_leakage": False, "swap_plausible": True,
        "name_aliases": [],
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
             "run_id": "demo", "repeat_id": repeat, "created_at": "2026-10-19T00:00:00Z"}
            for repeat in range(2) for t in trials]


class ExperimentTests(unittest.TestCase):
    def test_identity_changes_preserve_evidence_and_remove_source_identifiers(self):
        from wine_judgment_lab.experiment import build_trials
        trials = build_trials(dossiers(), rubric(), seed=19)
        self.assertEqual(len(trials), 4)
        states = {t["condition"]: t["state"] for t in trials}
        self.assertEqual(states["named"]["producer_identity"], "Domaine Example A")
        self.assertEqual(states["anonymous"]["producer_identity"], "Identity withheld")
        self.assertEqual(states["swapped"]["producer_identity"], "Domaine Example B")
        self.assertEqual(states["neutral"]["producer_identity"], "Domaine A")
        self.assertEqual(states["named"]["observations"], states["anonymous"]["observations"])
        self.assertEqual(states["named"]["observations"], states["swapped"]["observations"])
        self.assertNotIn("source_id", states["anonymous"]["observations"][0])
        self.assertNotIn("verification", states["anonymous"]["observations"][0])
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
        self.assertEqual(metric["paired_observations"], 2)
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
        self.assertEqual(sum(n for counts in metric["transitions"]["named_to_swapped"].values() for n in counts.values()), 0)

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

    def test_single_repeat_is_rejected_even_with_two_different_run_ids(self):
        from wine_judgment_lab.experiment import build_trials, analyze
        trials = build_trials(dossiers(), rubric(), seed=19)
        one = [r for r in judgments(trials) if r["repeat_id"] == 0]
        for results in (one, one + [dict(r, run_id="other") for r in one]):
            with self.assertRaisesRegex(ValueError, "two repeats"):
                analyze(trials, results)

    def test_repeat_variability_and_transition_counts_are_hand_checked(self):
        from wine_judgment_lab.experiment import build_trials, analyze
        trials = build_trials(dossiers(), rubric(), seed=19)
        conditions = {t["trial_id"]: t["condition"] for t in trials}
        results = judgments(trials)
        for row in results:
            condition = conditions[row["trial_id"]]
            if condition == "anonymous":
                row["label"] = "insufficient_evidence"
            if condition == "neutral" and row["repeat_id"] == 1:
                row["label"] = "contradicted"
        analyzed = analyze(trials, results)
        metric = analyzed["criteria"]["farming"]
        self.assertEqual(metric["same_trial_disagreement_rate"], 0.25)
        self.assertEqual(metric["same_trial_comparisons"], 4)
        self.assertEqual(metric["repeat_variability"]["neutral"]["disagreement_rate"], 1.0)
        self.assertEqual(metric["named_neutral_disagreement_rate"], 0.5)
        transitions = metric["transitions"]
        labels = ("supported", "contradicted", "insufficient_evidence")
        expected = {a: {b: 0 for b in labels} for a in labels}
        expected["supported"]["insufficient_evidence"] = 2
        self.assertEqual(transitions["named_to_anonymous"], expected)
        expected["supported"]["insufficient_evidence"] = 0
        expected["supported"]["supported"] = 1
        expected["supported"]["contradicted"] = 1
        self.assertEqual(transitions["named_to_neutral"], expected)
        expected["supported"]["supported"] = 2
        expected["supported"]["contradicted"] = 0
        self.assertEqual(transitions["named_to_swapped"], expected)

    def test_literal_names_are_flagged_case_insensitively_and_manual_flag_survives(self):
        from wine_judgment_lab.experiment import build_trials
        for text in ("A report about DOMAINE EXAMPLE A.", "A record for Domaine Example B."):
            rows = dossiers(); rows[0]["evidence"][0]["observation"] = text
            trials = build_trials(rows, rubric(), seed=19)
            self.assertTrue(all(t["automatic_identity_leakage"] and t["identity_leakage"] for t in trials))
        rows = dossiers(); rows[0]["identity_leakage"] = True
        trials = build_trials(rows, rubric(), seed=19)
        self.assertTrue(all(t["manual_identity_leakage"] and t["identity_leakage"] for t in trials))
        self.assertTrue(all(not t["automatic_identity_leakage"] for t in trials))

    def test_neutral_name_cannot_equal_real_or_swapped_identity(self):
        from wine_judgment_lab.experiment import build_trials
        for value in ("Domaine Example A", "domaine example b", "Identity withheld", ""):
            rows = dossiers(); rows[0]["neutral_name"] = value
            with self.assertRaises(ValueError):
                build_trials(rows, rubric(), seed=19)

    def test_three_repeats_compare_all_pairs_within_run_only(self):
        from wine_judgment_lab.experiment import build_trials, analyze
        trials = build_trials(dossiers(), rubric(), seed=19)
        results = judgments(trials)
        results += [dict(row, repeat_id=2) for row in results if row["repeat_id"] == 0]
        neutral_id = next(t["trial_id"] for t in trials if t["condition"] == "neutral")
        for row in results:
            if row["repeat_id"] == 1 and row["trial_id"] == neutral_id:
                row["label"] = "contradicted"
        # Two runs, each with three repeats: 2 × 4 trials × 3 pairs = 24.
        results += [dict(row, run_id="second") for row in results]
        analyzed = analyze(trials, results)
        self.assertEqual(analyzed["complete_runs"], 2)
        self.assertEqual(analyzed["complete_repeat_sets"], 6)
        metric = analyzed["criteria"]["farming"]
        self.assertEqual(metric["same_trial_comparisons"], 24)
        self.assertEqual(metric["repeat_variability"]["neutral"]["disagreements"], 4)
        self.assertAlmostEqual(metric["same_trial_disagreement_rate"], 1 / 6)

    def test_missing_neutral_variant_is_rejected(self):
        from wine_judgment_lab.experiment import build_trials, analyze
        trials = [t for t in build_trials(dossiers(), rubric(), seed=19) if t["condition"] != "neutral"]
        with self.assertRaises(ValueError):
            analyze(trials, judgments(trials))

    def test_reviewer_alias_matches_possessives_but_not_longer_words(self):
        from wine_judgment_lab.experiment import build_trials
        for text, expected in [("Northmere's parcels", True), ("NORTHMERE’s parcels", True),
                               ("Northmereish is a fictional adjective", False)]:
            rows = dossiers(); rows[0]["name_aliases"] = ["Northmere"]
            rows[0]["producer_name"] = "Domaine Northmere"
            rows[0]["evidence"][0]["observation"] = text
            trials = build_trials(rows, rubric(), seed=19)
            with self.subTest(text=text):
                self.assertTrue(all(t["automatic_identity_leakage"] == expected for t in trials))
                self.assertTrue(all(t["identity_leakage"] == expected for t in trials))
                self.assertTrue(all("name_aliases" not in t["state"] for t in trials))
                self.assertTrue(all("name_aliases" not in t for t in trials))
        rows[0]["identity_leakage"] = True
        self.assertTrue(all(t["identity_leakage"] for t in build_trials(rows, rubric(), seed=19)))

    def test_alias_list_must_be_explicit_and_well_formed(self):
        from wine_judgment_lab.experiment import build_trials
        for value in (None, "Northmere", [""], ["  "], [42]):
            rows = dossiers(); rows[0]["name_aliases"] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                build_trials(rows, rubric(), seed=19)
        rows = dossiers(); del rows[0]["name_aliases"]
        with self.assertRaises(ValueError):
            build_trials(rows, rubric(), seed=19)

    def test_clean_metrics_exclude_leaks_and_intersect_swap_plausibility(self):
        from wine_judgment_lab.experiment import build_trials, analyze
        rows = dossiers()
        leaky = copy.deepcopy(rows[0]); leaky.update(estate_id="leaky", identity_leakage=True)
        implausible = copy.deepcopy(rows[0]); implausible.update(estate_id="implausible", swap_plausible=False)
        trials = build_trials(rows + [leaky, implausible], rubric(), seed=19)
        index = {t["trial_id"]: t for t in trials}
        results = judgments(trials)
        for row in results:
            trial = index[row["trial_id"]]
            if trial["estate_id"] == "leaky":
                if trial["condition"] == "anonymous": row["label"] = "insufficient_evidence"
                if trial["condition"] == "neutral": row["label"] = "insufficient_evidence"
                if trial["condition"] == "swapped": row["label"] = "contradicted"
                if trial["condition"] == "named" and row["repeat_id"] == 1: row["label"] = "contradicted"
            if trial["estate_id"] == "implausible":
                if trial["condition"] == "neutral": row["label"] = "insufficient_evidence"
                if trial["condition"] == "swapped": row["label"] = "contradicted"
        all_metrics = analyze(trials, results)["criteria"]["farming"]
        self.assertAlmostEqual(all_metrics["named_neutral_disagreement_rate"], 2 / 3)
        clean = all_metrics["clean_subset"]
        self.assertEqual(clean["estate_count"], 2)
        self.assertEqual(clean["paired_observations"], 4)
        self.assertEqual(clean["named_neutral_disagreement_rate"], 0.5)
        self.assertEqual(clean["named_anonymous_disagreement_rate"], 0)
        self.assertEqual(clean["swapped_named_disagreement_rate"], 0)
        self.assertEqual(clean["swapped_paired_observations"], 2)
        self.assertEqual(clean["same_trial_comparisons"], 8)
        self.assertEqual(clean["same_trial_disagreement_rate"], 0)
        self.assertAlmostEqual(all_metrics["same_trial_disagreement_rate"], 1 / 12)
        self.assertEqual(clean["insufficient_evidence_rate"], 1 / 8)
        for condition in ("named", "anonymous", "neutral", "swapped"):
            self.assertEqual(clean["repeat_variability"][condition],
                             {"comparisons": 2, "disagreements": 0, "disagreement_rate": 0})
        labels = ("supported", "contradicted", "insufficient_evidence")
        for comparison in ("anonymous", "neutral", "swapped"):
            expected = {a: {b: 0 for b in labels} for a in labels}
            expected["supported"]["supported"] = 4 if comparison == "anonymous" else 2
            if comparison == "neutral": expected["supported"]["insufficient_evidence"] = 2
            self.assertEqual(clean["transitions"]["named_to_" + comparison], expected)
        # Completeness is checked on all input, before any clean-subset filtering.
        incomplete = [r for r in results if not (index[r["trial_id"]]["estate_id"] == "leaky"
                                                and r["repeat_id"] == 1
                                                and index[r["trial_id"]]["condition"] == "neutral")]
        with self.assertRaises(ValueError):
            analyze(trials, incomplete)

    def test_empty_clean_subset_has_null_rates_and_zero_counts(self):
        from wine_judgment_lab.experiment import build_trials, analyze
        rows = dossiers(); rows[0]["identity_leakage"] = True
        trials = build_trials(rows, rubric(), seed=19)
        clean = analyze(trials, judgments(trials))["criteria"]["farming"]["clean_subset"]
        self.assertEqual(clean["estate_count"], 0)
        self.assertEqual(clean["paired_observations"], 0)
        self.assertEqual(clean["swapped_paired_observations"], 0)
        self.assertEqual(clean["same_trial_comparisons"], 0)
        for key in ("named_anonymous_disagreement_rate", "named_neutral_disagreement_rate",
                    "swapped_named_disagreement_rate", "same_trial_disagreement_rate", "insufficient_evidence_rate"):
            self.assertIsNone(clean[key])
        for values in clean["repeat_variability"].values():
            self.assertEqual(values, {"comparisons": 0, "disagreements": 0, "disagreement_rate": None})
        for table in clean["transitions"].values():
            self.assertEqual(sum(len(counts) for counts in table.values()), 9)
            self.assertEqual(sum(n for counts in table.values() for n in counts.values()), 0)


if __name__ == "__main__":
    unittest.main()
