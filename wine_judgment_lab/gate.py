"""Sufficiency-gate audit: who qualifies to be ranked, by identity condition.

A ranking with an evidence-sufficiency cutoff makes two decisions: how it
scores each dossier and whose evidence it accepts as enough. This module
audits the second one across conditions (e.g. named vs masked), cutoffs and
repeats. Descriptive only: no causal claims, no model calls.
"""
from itertools import combinations
from math import comb, isfinite
from statistics import median

DEFAULT_CUTOFFS = (0.60, 0.65, 0.70, 0.75, 0.80)
# Medians of two repeats (0.71, 0.69) must still meet a 0.70 cutoff exactly.
TOLERANCE = 1e-9


def _round(value):
    return None if value is None else round(value, 4)


def _meets(value, cutoff):
    return value >= cutoff - TOLERANCE


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _number(value):
    return not isinstance(value, bool) and isinstance(value, (int, float)) and isfinite(value)


def _ranks(values):
    """Average ranks (1 = smallest), ties sharing their mean rank."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        for k in range(i, j + 1):
            ranks[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return ranks


def spearman(xs, ys):
    if len(xs) != len(ys) or len(xs) < 3:
        return None
    rx, ry = _ranks(xs), _ranks(ys)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    cov = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    vx, vy = sum((a - mx) ** 2 for a in rx), sum((b - my) ** 2 for b in ry)
    return None if not vx or not vy else cov / (vx * vy) ** 0.5


def sign_test(down, up):
    """Exact two-sided binomial sign test; ties are excluded by the caller."""
    n = down + up
    if not n:
        return None
    tail = sum(comb(n, i) for i in range(min(down, up) + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def _validate(rows, *, min_repeats):
    if not isinstance(rows, list) or not rows:
        raise ValueError("At least one gate judgment is required")
    cells, judges, kinds = {}, set(), set()
    for row in rows:
        if not isinstance(row, dict) or any(not _text(row.get(k)) for k in
                                            ("entity_id", "condition", "provider", "model", "run_id")):
            raise ValueError("Each judgment needs entity_id, condition, provider, model and run_id")
        if type(row.get("repeat_id")) is not int or row["repeat_id"] < 0:
            raise ValueError("repeat_id must be a nonnegative integer")
        if not _number(row.get("score")):
            raise ValueError("score must be a finite number")
        if not _number(row.get("sufficiency")) or not 0 <= row["sufficiency"] <= 1:
            raise ValueError("sufficiency must be a number from 0 to 1")
        if type(row.get("synthetic")) is not bool:
            raise ValueError("synthetic must be an explicit boolean")
        key = (row["entity_id"], row["condition"], row["run_id"], row["repeat_id"])
        if key in cells:
            raise ValueError("Duplicate judgment for one entity, condition, run and repeat")
        cells[key] = row
        judges.add((row["provider"], row["model"]))
        kinds.add(row["synthetic"])
    if len(judges) != 1:
        raise ValueError("Analyze each provider/model separately")
    entities = sorted({k[0] for k in cells})
    conditions = sorted({k[1] for k in cells})
    repeats = sorted({(k[2], k[3]) for k in cells})
    # Every entity needs every condition in every repeat, or comparisons are uneven.
    missing = [(e, c, r) for e in entities for c in conditions for r in repeats if (e, c, *r) not in cells]
    if missing:
        raise ValueError(f"Incomplete design: {len(missing)} entity/condition/repeat cells are missing")
    if len(repeats) < min_repeats:
        raise ValueError(f"At least {min_repeats} repeats are required; found {len(repeats)}")
    return cells, entities, conditions, repeats, next(iter(judges)), kinds == {True}


def _cutoffs(values):
    cutoffs = sorted(set(values))
    if not cutoffs or any(not _number(c) or not 0 < c <= 1 for c in cutoffs):
        raise ValueError("Cutoffs must be numbers in (0, 1]")
    return cutoffs


def gate_audit(rows, *, reference="named", cutoffs=DEFAULT_CUTOFFS, band=0.03,
               min_repeats=2, leaks=None, external_ranks=None):
    """Compare who qualifies under each condition against a reference condition.

    An entity qualifies at a cutoff when its median sufficiency across repeats
    reaches the cutoff. leaks maps entity_id -> bool (True = identity leaks);
    external_ranks maps entity_id -> rank (1 = best), oriented so that a
    positive correlation always means agreement.
    """
    cells, entities, conditions, repeats, judge, synthetic = _validate(rows, min_repeats=min_repeats)
    cutoffs = _cutoffs(cutoffs)
    if reference not in conditions:
        raise ValueError(f"Reference condition {reference!r} is not in the data")
    if not _number(band) or not 0 <= band < 1:
        raise ValueError("band must be a number from 0 to 1")
    leaks = dict(leaks or {})
    if set(leaks) - set(entities) or any(type(v) is not bool for v in leaks.values()):
        raise ValueError("leaks must map known entity IDs to booleans")
    external = dict(external_ranks or {})
    if set(external) - set(entities) or any(not _number(v) for v in external.values()):
        raise ValueError("external_ranks must map known entity IDs to numeric ranks")

    def values(entity, condition, field):
        return [cells[(entity, condition, *r)][field] for r in repeats]

    med = {(e, c, f): median(values(e, c, f)) for e in entities for c in conditions for f in ("score", "sufficiency")}

    def population(ids):
        out = {"entity_count": len(ids), "conditions": {}, "comparisons": {}}
        for c in conditions:
            per_cutoff = {}
            for cut in cutoffs:
                qualified = [e for e in ids if _meets(med[(e, c, "sufficiency")], cut)]
                leader = max(qualified, key=lambda e: (med[(e, c, "score")], e), default=None)
                # Gate noise: entities whose qualification differs between repeats.
                unstable = [e for e in ids if len({_meets(s, cut) for s in values(e, c, "sufficiency")}) > 1]
                per_cutoff[f"{cut:.2f}"] = {"qualified": len(qualified), "leader": leader,
                                            "unstable_across_repeats": len(unstable)}
            diffs = [abs(a - b) for e in ids for a, b in combinations(values(e, c, "sufficiency"), 2)]
            unfiltered = max(ids, key=lambda e: (med[(e, c, "score")], e), default=None)
            out["conditions"][c] = {
                "leader_without_cutoff": unfiltered, "by_cutoff": per_cutoff,
                "median_repeat_sufficiency_difference": _round(median(diffs)) if diffs else None,
            }
            if external and len(ids) >= 3 and all(e in external for e in ids):
                # Negate ranks so that agreement (high score, rank 1) is positive.
                out["conditions"][c]["spearman_with_external_ranks"] = _round(spearman(
                    [med[(e, c, "score")] for e in ids], [-external[e] for e in ids]))
        for c in conditions:
            if c == reference:
                continue
            shifts = [med[(e, c, "sufficiency")] - med[(e, reference, "sufficiency")] for e in ids]
            down, up = sum(s < 0 for s in shifts), sum(s > 0 for s in shifts)
            gates = {}
            for cut in cutoffs:
                ref_q = {e for e in ids if _meets(med[(e, reference, "sufficiency")], cut)}
                cmp_q = {e for e in ids if _meets(med[(e, c, "sufficiency")], cut)}
                near = [e for e in ids if abs(med[(e, reference, "sufficiency")] - cut) <= band + TOLERANCE]
                gates[f"{cut:.2f}"] = {f"only_{reference}": len(ref_q - cmp_q), f"only_{c}": len(cmp_q - ref_q),
                                       "both": len(ref_q & cmp_q), f"near_cutoff_in_{reference}": len(near)}
            out["comparisons"][f"{reference}_vs_{c}"] = {
                "qualification_by_cutoff": gates,
                "sufficiency_shift": {"median": _round(median(shifts)) if shifts else None, "down": down, "up": up,
                                      "unchanged": len(shifts) - down - up,
                                      "sign_test_two_sided_p": _round(sign_test(down, up))},
                "score": {"spearman_all_entities": _round(spearman([med[(e, reference, "score")] for e in ids],
                                                                   [med[(e, c, "score")] for e in ids])),
                          "median_absolute_shift": _round(median(abs(med[(e, c, "score")] - med[(e, reference, "score")])
                                                                 for e in ids)) if ids else None},
            }
        return out

    clean = [e for e in entities if not leaks.get(e, False)]
    return {
        "data_kind": "synthetic" if synthetic else "contains_real_data",
        "provider": judge[0], "model": judge[1],
        "reference_condition": reference, "cutoffs": [f"{c:.2f}" for c in cutoffs], "near_cutoff_band": band,
        "repeat_count": len(repeats), "exploratory_single_repeat": len(repeats) == 1,
        "qualification_rule": "median sufficiency across repeats is at or above the cutoff",
        "all": population(entities),
        "clean": population(clean) if leaks else None,
        "interpretation": ("Descriptive gate audit. Qualification differences between conditions are only "
                           "informative beside repeat instability and near-cutoff counts. Entity IDs here are "
                           "private analysis output; publish aggregates only."),
    }
