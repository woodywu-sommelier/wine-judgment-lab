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

    def test_baseline_is_fit_only_on_training_tiers(self):
        from wine_judgment_lab.audit import evaluate_baseline, assign_splits
        original = rows()
        split = assign_splits(original, seed=19)
        result = evaluate_baseline(original, seed=19)["regions"]["Burgundy"]
        self.assertEqual(result["training_modal_tier"], 0)
        self.assertEqual(result["training_tier_counts"], {0: 1, 1: 1, 2: 1, 3: 1})

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

    def test_every_non_singleton_tier_has_train_and_test_estates(self):
        from wine_judgment_lab.audit import assign_splits
        for seed in range(12):
            data = rows() + [dict(rows()[3], estate_id="third-three")]
            split = assign_splits(data, seed=seed)
            for tier in range(4):
                self.assertEqual({split[r["estate_id"]] for r in data if r["tier"] == tier}, {"train", "test"})

    def test_singleton_is_retained_and_reported_not_evaluable(self):
        from wine_judgment_lab.audit import evaluate_baseline
        data = [r for r in rows() if r["estate_id"] != "fiction-7"]
        result = evaluate_baseline(data, seed=19)
        self.assertEqual(result["splits"]["fiction-3"], "train")
        tier = result["regions"]["Burgundy"]["per_tier"][3]
        self.assertEqual(tier, {"train_n": 1, "test_n": 0, "status": "not_evaluable", "heldout": None})

    def test_all_singletons_have_no_heldout_score(self):
        from wine_judgment_lab.audit import evaluate_baseline
        region = evaluate_baseline(rows()[:4], seed=19)["regions"]["Burgundy"]
        self.assertEqual(region["test_n"], 0)
        self.assertIsNone(region["heldout"])
        self.assertTrue(all(t["status"] == "not_evaluable" for t in region["per_tier"].values()))


if __name__ == "__main__":
    unittest.main()
