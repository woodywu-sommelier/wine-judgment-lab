import copy
import unittest


def rows():
    return [{"estate_id": f"fiction-{i}", "region": "Burgundy", "tier": i % 4,
             "reference_price": None if i == 0 else 30 + i, "price_observed_at": None if i == 0 else "2026-06-01",
             "award_published_at": "2026-07-07", "critic_coverage": "not_searched", "synthetic": True}
            for i in range(8)]


class AuditTests(unittest.TestCase):
    def test_split_is_disjoint_and_order_invariant(self):
        from wine_judgment_lab.audit import assign_splits
        first = assign_splits(rows(), seed=19)
        self.assertEqual(first, assign_splits(list(reversed(rows())), seed=19))
        self.assertEqual(set(first.values()), {"train", "test"})
        self.assertEqual(len(first), 8)

    def test_prices_must_be_positive_finite_and_strictly_before_awards(self):
        from wine_judgment_lab.audit import validate_audit
        for price in (float("nan"), float("inf"), -1, 0, True):
            bad = rows(); bad[1]["reference_price"] = price
            with self.subTest(price=price), self.assertRaises(ValueError):
                validate_audit(bad)
        for observed in ("2026-07-07", "2026-07-08", None):
            bad = rows(); bad[1]["price_observed_at"] = observed
            with self.subTest(observed=observed), self.assertRaises(ValueError):
                validate_audit(bad)

    def test_duplicate_estates_and_invalid_tiers_fail(self):
        from wine_judgment_lab.audit import validate_audit
        with self.assertRaises(ValueError):
            validate_audit(rows() + [rows()[0]])
        bad = rows(); bad[0]["tier"] = 4
        with self.assertRaises(ValueError):
            validate_audit(bad)

    def test_heldout_truth_does_not_change_fitted_baseline(self):
        from wine_judgment_lab.audit import evaluate_baseline, assign_splits
        original = rows()
        split = assign_splits(original, seed=19)
        changed = copy.deepcopy(original)
        for row in changed:
            if split[row["estate_id"]] == "test": row["tier"] = 3
        before = evaluate_baseline(original, seed=19)["regions"]["Burgundy"]
        after = evaluate_baseline(changed, seed=19)["regions"]["Burgundy"]
        self.assertEqual(before["training_modal_tier"], after["training_modal_tier"])

    def test_tier_metrics_use_hand_checked_values(self):
        from wine_judgment_lab.audit import tier_metrics
        result = tier_metrics([0, 2], [0, 0])
        self.assertEqual(result["accuracy"], 0.5)
        self.assertEqual(result["mean_absolute_tier_error"], 1.0)
        self.assertAlmostEqual(result["macro_f1_observed_labels"], 1 / 3)

    def test_regions_are_evaluated_separately_and_tiny_regions_fail(self):
        from wine_judgment_lab.audit import evaluate_baseline
        bad = rows(); bad[0]["region"] = "Bordeaux"
        with self.assertRaises(ValueError):
            evaluate_baseline(bad, seed=19)


if __name__ == "__main__":
    unittest.main()
