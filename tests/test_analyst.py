import copy
import unittest

from test_experiment import dossiers, rubric


def adjudicated():
    rows = dossiers()
    rows[0]["analyst_assessments"][0].update(expected_label="supported",
        adjudicated_by=["Fictional reviewer A", "Fictional reviewer B"],
        adjudicated_at="2026-10-19", agreement="consensus")
    return rows


class AnalystTests(unittest.TestCase):
    def test_exactly_one_assessment_per_rubric_criterion(self):
        from wine_judgment_lab.experiment import build_trials
        for assessments in (None, [], dossiers()[0]["analyst_assessments"] * 2,
                            [dict(dossiers()[0]["analyst_assessments"][0], criterion_id="unknown")]):
            rows = dossiers(); rows[0]["analyst_assessments"] = assessments
            with self.subTest(assessments=assessments), self.assertRaises(ValueError):
                build_trials(rows, rubric(), seed=19)

    def test_absent_criterion_in_an_empty_dossier_is_explicit(self):
        from wine_judgment_lab.experiment import build_trials
        rows = dossiers(); rows[0]["evidence"] = []; rows[0]["sources"] = []
        rows[0]["analyst_assessments"][0]["completeness"] = "absent"
        self.assertEqual(len(build_trials(rows, rubric(), seed=19)), 4)
        rows[0]["analyst_assessments"] = []
        with self.assertRaises(ValueError):
            build_trials(rows, rubric(), seed=19)

    def test_invalid_status_label_and_adjudication_fields_are_rejected(self):
        from wine_judgment_lab.experiment import build_trials
        for key, value in (("completeness", "missing"), ("expected_label", "excellent"),
                           ("adjudicated_by", "WW"), ("adjudicated_at", "not-a-date"),
                           ("agreement", "guessed"), ("note", None)):
            rows = dossiers(); rows[0]["analyst_assessments"][0][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                build_trials(rows, rubric(), seed=19)
        for key in ("expected_label", "completeness", "adjudicated_by", "adjudicated_at", "agreement", "note"):
            rows = dossiers(); del rows[0]["analyst_assessments"][0][key]
            with self.subTest(missing=key), self.assertRaises(ValueError):
                build_trials(rows, rubric(), seed=19)

    def test_analyst_edits_leave_all_frozen_trial_fields_unchanged(self):
        from wine_judgment_lab.experiment import build_trials
        rows = adjudicated()
        before = build_trials(rows, rubric(), seed=19)
        for key, value in (("expected_label", "insufficient_evidence"), ("completeness", "conflicting")):
            changed = copy.deepcopy(rows); changed[0]["analyst_assessments"][0][key] = value
            after = build_trials(changed, rubric(), seed=19)
            self.assertEqual(before, after)  # stronger than just IDs and hashes

    def test_pending_labels_fail_reference_readiness_but_not_trial_preparation(self):
        from wine_judgment_lab.experiment import build_trials
        from wine_judgment_lab.analyst import check_reference_ready
        rows = dossiers()
        self.assertEqual(len(build_trials(rows, rubric(), seed=19)), 4)
        with self.assertRaisesRegex(ValueError, "not adjudicated"):
            check_reference_ready(rows, {"farming"}, first_run_at="2026-10-21T12:00:00Z")

    def test_reference_labels_require_attribution_and_agreement(self):
        from wine_judgment_lab.experiment import build_trials
        for key, value in (("adjudicated_by", []), ("adjudicated_by", ["A", "A"]),
                           ("adjudicated_at", None), ("agreement", None)):
            rows = adjudicated(); rows[0]["analyst_assessments"][0][key] = value
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                build_trials(rows, rubric(), seed=19)

    def test_adjudication_must_precede_first_run_and_timestamp_needs_timezone(self):
        from wine_judgment_lab.analyst import check_reference_ready
        rows = adjudicated()
        self.assertEqual(check_reference_ready(rows, {"farming"}, first_run_at="2026-10-20T00:00:00Z")["assessment_count"], 1)
        for stamp in ("2026-10-19", "2026-10-21", "2026-10-20T12:00:00Z"):
            rows[0]["analyst_assessments"][0]["adjudicated_at"] = stamp
            with self.subTest(stamp=stamp), self.assertRaises(ValueError):
                check_reference_ready(rows, {"farming"}, first_run_at="2026-10-19T23:00:00Z")
        rows = adjudicated()
        rows[0]["analyst_assessments"][0]["adjudicated_at"] = "2026-10-20T11:59:59+00:00"
        self.assertEqual(check_reference_ready(rows, {"farming"}, first_run_at="2026-10-20T12:00:00Z")["assessment_count"], 1)
        for first in ("2026-10-20", "2026-10-20T12:00:00"):
            with self.assertRaises(ValueError):
                check_reference_ready(rows, {"farming"}, first_run_at=first)

    def test_mismatch_is_flagged_without_changing_any_reference_label(self):
        from wine_judgment_lab.analyst import validate_assessments, check_reference_ready
        rows = adjudicated(); rows[0]["analyst_assessments"][0]["completeness"] = "absent"
        before = copy.deepcopy(rows)
        flags = validate_assessments(rows[0], {"farming"})
        self.assertIn("completeness_label_mismatch", [f["code"] for f in flags])
        self.assertIn("absent_with_observations", [f["code"] for f in flags])
        report = check_reference_ready(rows, {"farming"}, first_run_at="2026-10-20T12:00:00Z")
        self.assertEqual(report["review_flags"], flags)
        self.assertEqual(rows, before)


if __name__ == "__main__":
    unittest.main()
