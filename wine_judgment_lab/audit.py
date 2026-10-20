"""Estate-level held-out baseline for an information audit; no causal claims."""
from collections import Counter, defaultdict
from datetime import date
import hashlib
import math


def validate_audit(rows):
    if not isinstance(rows, list) or not rows:
        raise ValueError("At least one audit row is required")
    ids = set()
    for row in rows:
        if any(not isinstance(row.get(k), str) or not row[k].strip() for k in ("estate_id", "region")):
            raise ValueError("estate_id and region must be nonempty strings")
        if row["estate_id"] in ids:
            raise ValueError("Aggregate observations to one row per estate before splitting")
        ids.add(row["estate_id"])
        if type(row.get("tier")) is not int or row["tier"] not in range(4):
            raise ValueError("Tier must be 0 Selected, 1, 2 or 3")
        if type(row.get("synthetic")) is not bool:
            raise ValueError("Synthetic status must be explicit")
        if row.get("critic_coverage") not in {"found", "searched_not_found", "not_searched"}:
            raise ValueError("Unknown critic coverage state")
        published = date.fromisoformat(row["award_published_at"])
        price = row.get("reference_price")
        observed = row.get("price_observed_at")
        if price is None:
            if observed is not None:
                raise ValueError("A missing price cannot have an observation date")
        else:
            if isinstance(price, bool) or not isinstance(price, (float, int)) or not math.isfinite(price) or price <= 0:
                raise ValueError("Prices must be positive finite numbers or null")
            if not isinstance(observed, str) or date.fromisoformat(observed) >= published:
                raise ValueError("Prices must be observed strictly before the award announcement")


def assign_splits(rows, *, seed):
    validate_audit(rows)
    regions = defaultdict(list)
    for row in rows:
        regions[row["region"]].append(row["estate_id"])
    result = {}
    for region, ids in sorted(regions.items()):
        if len(ids) < 2:
            raise ValueError(f"Region {region} needs at least two estates for a split")
        for tier in range(4):
            members = [r["estate_id"] for r in rows if r["region"] == region and r["tier"] == tier]
            members.sort(key=lambda estate: hashlib.sha256(f"{seed}\0{region}\0{tier}\0{estate}".encode()).hexdigest())
            test_count = max(1, len(members) // 4) if len(members) >= 2 else 0
            result.update({estate: "test" if i < test_count else "train" for i, estate in enumerate(members)})
    return result


def tier_metrics(truth, predictions):
    if not truth or len(truth) != len(predictions):
        raise ValueError("Truth and predictions must be nonempty and aligned")
    if any(type(v) is not int or v not in range(4) for v in truth + predictions):
        raise ValueError("Tiers must be integers from zero through three")
    f1 = []
    for label in sorted(set(truth) | set(predictions)):
        tp = sum(y == p == label for y, p in zip(truth, predictions))
        fp = sum(y != label and p == label for y, p in zip(truth, predictions))
        fn = sum(y == label and p != label for y, p in zip(truth, predictions))
        f1.append(2 * tp / (2 * tp + fp + fn))
    return {"n": len(truth), "accuracy": sum(y == p for y, p in zip(truth, predictions)) / len(truth),
            "mean_absolute_tier_error": sum(abs(y - p) for y, p in zip(truth, predictions)) / len(truth),
            "macro_f1_observed_labels": sum(f1) / len(f1)}


def evaluate_baseline(rows, *, seed):
    split = assign_splits(rows, seed=seed)
    regions = {}
    for region in sorted({r["region"] for r in rows}):
        train = [r for r in rows if r["region"] == region and split[r["estate_id"]] == "train"]
        test = [r for r in rows if r["region"] == region and split[r["estate_id"]] == "test"]
        counts = Counter(r["tier"] for r in train)
        modal = min(counts, key=lambda label: (-counts[label], label))
        per_tier = {}
        for tier in range(4):
            heldout = [r for r in test if r["tier"] == tier]
            per_tier[tier] = {"train_n": counts[tier], "test_n": len(heldout),
                              "status": "evaluable" if heldout else "not_evaluable",
                              "heldout": tier_metrics([tier] * len(heldout), [modal] * len(heldout)) if heldout else None}
        regions[region] = {"training_modal_tier": modal, "train_n": len(train), "test_n": len(test),
                           "training_tier_counts": dict(sorted(counts.items())),
                           "per_tier": per_tier,
                           "heldout": tier_metrics([r["tier"] for r in test], [modal] * len(test)) if test else None}
    return {"data_kind": "synthetic" if all(r["synthetic"] for r in rows) else "contains_real_data",
            "method": "training-only modal tier baseline; ordinal regression not fitted",
            "seed": seed, "splits": dict(sorted(split.items())), "regions": regions,
            "interpretation": "Predictability within selected estates, not quality or causal bias."}
