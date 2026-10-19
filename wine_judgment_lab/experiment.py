"""Identity variants and paired categorical evidence judgments, with provenance."""
from __future__ import annotations

import copy
import hashlib
import json
from collections import defaultdict
from datetime import datetime

LABELS = {"supported", "contradicted", "insufficient_evidence"}
CONDITIONS = ("named", "anonymous", "swapped")


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def validate_dossiers(rows):
    if not isinstance(rows, list) or not rows:
        raise ValueError("At least one dossier is required")
    ids = set()
    for row in rows:
        if not isinstance(row, dict) or any(not _text(row.get(k)) for k in
                                           ("estate_id", "producer_name", "swap_name", "region")):
            raise ValueError("Dossier identity fields must be nonempty strings")
        if row["estate_id"] in ids:
            raise ValueError("Duplicate estate_id")
        ids.add(row["estate_id"])
        if row["producer_name"] == row["swap_name"]:
            raise ValueError("The swapped name must differ")
        if any(type(row.get(k)) is not bool for k in ("synthetic", "identity_leakage", "swap_plausible")):
            raise ValueError("synthetic, identity_leakage and swap_plausible must be explicit booleans")
        if not isinstance(row.get("sources"), list) or not isinstance(row.get("evidence"), list):
            raise ValueError("sources and evidence must be lists")
        sources = {}
        for source in row["sources"]:
            if not isinstance(source, dict) or any(not _text(source.get(k)) for k in ("source_id", "url", "rights")):
                raise ValueError("Each source needs an ID, URL and rights status")
            if source["source_id"] in sources:
                raise ValueError("Duplicate source_id")
            sources[source["source_id"]] = source
        for item in row["evidence"]:
            if not isinstance(item, dict) or any(not _text(item.get(k)) for k in ("criterion_id", "observation", "source_id")):
                raise ValueError("Each observation needs criterion, text and source")
            if item.get("verification") not in {"independent", "producer_claim", "missing"}:
                raise ValueError("Unknown verification status")
            if item["source_id"] not in sources:
                raise ValueError("Unknown evidence source")


def _validate_rubric(rubric):
    if not isinstance(rubric, dict) or not _text(rubric.get("version")) or not rubric.get("questions"):
        raise ValueError("A versioned rubric with questions is required")
    ids = set()
    for question in rubric["questions"]:
        criterion = question.get("criterion_id")
        if not _text(criterion) or criterion in ids or not _text(question.get("instructions")):
            raise ValueError("Rubric criterion IDs must be unique and instructions explicit")
        if not isinstance(question.get("labels"), dict) or set(question["labels"]) != LABELS:
            raise ValueError("Rubric must use the three registered evidence labels")
        if any(not _text(v) for v in question["labels"].values()):
            raise ValueError("Every label needs a definition")
        ids.add(criterion)
    return ids


def build_trials(rows, rubric, *, seed):
    validate_dossiers(rows)
    criteria = _validate_rubric(rubric)
    trials = []
    for row in sorted(rows, key=lambda r: r["estate_id"]):
        observations = []
        for item in row["evidence"]:
            if item["criterion_id"] not in criteria:
                raise ValueError("Evidence references an unknown criterion")
            observations.append({"criterion_id": item["criterion_id"], "text": item["observation"],
                                 "verification": item["verification"]})
        observations.sort(key=lambda x: (x["criterion_id"], x["text"], x["verification"]))
        for condition in CONDITIONS:
            trial_id = digest([seed, row["estate_id"], condition])[:24]
            identity = {"named": row["producer_name"], "anonymous": "Identity withheld", "swapped": row["swap_name"]}[condition]
            trial = {"trial_id": trial_id, "estate_id": row["estate_id"], "condition": condition,
                     "synthetic": row["synthetic"], "identity_leakage": row["identity_leakage"],
                     "swap_plausible": row["swap_plausible"], "evidence_hash": digest(observations),
                     "rubric_hash": digest(rubric), "state": {"producer_identity": identity,
                     "region": row["region"], "observations": copy.deepcopy(observations)},
                     "questions": copy.deepcopy(rubric["questions"])}
            trial["trial_hash"] = digest(trial)
            trials.append(trial)
    # Hash ordering is reproducible across Python versions and input row order.
    return sorted(trials, key=lambda t: digest([seed, "order", t["trial_id"]]))


def _rate(values):
    return sum(values) / len(values) if values else None


def analyze(trials, judgments):
    if not trials or not judgments:
        raise ValueError("Trials and complete judgments are required")
    index = {}
    estate_conditions = defaultdict(set)
    estate_evidence = {}
    for trial in trials:
        if trial.get("trial_hash") != digest({k: v for k, v in trial.items() if k != "trial_hash"}):
            raise ValueError("Trial has been edited or its hash is invalid")
        if trial["trial_id"] in index or trial["condition"] not in CONDITIONS:
            raise ValueError("Invalid or duplicate trial")
        if trial["condition"] in estate_conditions[trial["estate_id"]]:
            raise ValueError("Each estate must have exactly one trial per identity condition")
        if trial["evidence_hash"] != digest(trial["state"]["observations"]):
            raise ValueError("Observation hash is invalid")
        _validate_rubric({"version": "imported", "questions": trial["questions"]})
        comparable = digest({"region": trial["state"]["region"], "observations": trial["state"]["observations"],
                             "questions": trial["questions"], "rubric_hash": trial["rubric_hash"],
                             "identity_leakage": trial["identity_leakage"], "swap_plausible": trial["swap_plausible"],
                             "synthetic": trial["synthetic"]})
        previous = estate_evidence.setdefault(trial["estate_id"], comparable)
        if previous != comparable:
            raise ValueError("Variants must share evidence, region, rubric and reviewer flags")
        index[trial["trial_id"]] = trial
        estate_conditions[trial["estate_id"]].add(trial["condition"])
    if any(conditions != set(CONDITIONS) for conditions in estate_conditions.values()):
        raise ValueError("Every estate must have all three identity variants")
    expected = {(t["trial_id"], q["criterion_id"]) for t in trials for q in t["questions"]}
    groups = defaultdict(dict)
    for row in judgments:
        if any(not _text(row.get(k)) for k in ("trial_id", "trial_hash", "criterion_id", "provider", "model", "run_id", "created_at")):
            raise ValueError("Judgment provenance is incomplete")
        if type(row.get("repeat_id")) is not int or row["repeat_id"] < 0:
            raise ValueError("repeat_id must be a nonnegative integer")
        stamp = datetime.fromisoformat(row["created_at"].replace("Z", "+00:00"))
        if stamp.tzinfo is None:
            raise ValueError("Judgment timestamp needs a timezone")
        trial = index.get(row["trial_id"])
        pair = (row["trial_id"], row["criterion_id"])
        if trial is None or row["trial_hash"] != trial["trial_hash"] or pair not in expected:
            raise ValueError("Judgment does not match the frozen trial")
        if row.get("label") not in LABELS:
            raise ValueError("Invalid evidence label")
        group = (row["provider"], row["model"], row["run_id"], row["repeat_id"])
        if pair in groups[group]:
            raise ValueError("Duplicate judgment")
        groups[group][pair] = row["label"]
    if any(set(values) != expected for values in groups.values()):
        raise ValueError("Every model/run/repeat needs a complete trial-by-criterion set")
    # Do not pool different judges into a single apparent effect.
    judges = {(g[0], g[1]) for g in groups}
    if len(judges) != 1:
        raise ValueError("Analyze each provider/model separately")
    by_estate = defaultdict(dict)
    for t in trials:
        by_estate[t["estate_id"]][t["condition"]] = t
    aggregates = defaultdict(lambda: {"all": [], "clean": [], "swapped": [], "labels": []})
    for values in groups.values():
        for variants in by_estate.values():
            named, anonymous, swapped = (variants[c] for c in CONDITIONS)
            for q in named["questions"]:
                c = q["criterion_id"]
                labels = [values[(t["trial_id"], c)] for t in (named, anonymous, swapped)]
                agg = aggregates[c]
                agg["all"].append(labels[0] != labels[1])
                if not named["identity_leakage"]:
                    agg["clean"].append(labels[0] != labels[1])
                if named["swap_plausible"]:
                    agg["swapped"].append(labels[2] != labels[0])
                agg["labels"].extend(labels)
    criteria = {c: {"paired_observations": len(a["all"]), "clean_paired_observations": len(a["clean"]),
                    "named_anonymous_disagreement_rate": _rate(a["all"]),
                    "clean_named_anonymous_disagreement_rate": _rate(a["clean"]),
                    "swapped_named_disagreement_rate": _rate(a["swapped"]),
                    "insufficient_evidence_rate": _rate([v == "insufficient_evidence" for v in a["labels"]])}
                for c, a in sorted(aggregates.items())}
    return {"data_kind": "synthetic" if all(t["synthetic"] for t in trials) else "contains_real_data",
            "estate_count": len(by_estate), "complete_runs": len(groups),
            "provider": next(iter(judges))[0], "model": next(iter(judges))[1], "criteria": criteria,
            "interpretation": "Descriptive label sensitivity only; repeated pairs are not independent estates."}
