"""Private criterion assessments and pre-inference reference-readiness checks."""
from datetime import date, datetime, time, UTC

LABELS = {"supported", "contradicted", "insufficient_evidence"}
COMPLETENESS = {"absent", "partial", "conflicting", "adequate"}
AGREEMENTS = {"consensus", "majority", "adjudicator_decision", "single_reviewer"}


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _timestamp(value):
    if not isinstance(value, str) or "T" not in value:
        raise ValueError("Run/adjudication timestamp requires a time and timezone")
    stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if stamp.tzinfo is None:
        raise ValueError("Run/adjudication timestamp requires a timezone")
    return stamp.astimezone(UTC)


def _adjudication_time(value):
    if isinstance(value, str) and len(value) == 10:
        # A date cannot establish ordering within the same UTC day.
        return datetime.combine(date.fromisoformat(value), time.max, tzinfo=UTC)
    return _timestamp(value)


def validate_assessments(dossier, criterion_ids):
    """Validate exactly one assessment per criterion; return non-mutating warnings."""
    assessments = dossier.get("analyst_assessments")
    if not isinstance(assessments, list):
        raise ValueError("analyst_assessments must be an explicit list")
    required = {"criterion_id", "completeness", "expected_label", "adjudicated_by",
                "adjudicated_at", "agreement", "note"}
    seen, flags = set(), []
    for item in assessments:
        if not isinstance(item, dict) or set(item) != required:
            raise ValueError("Assessment requires exactly the documented private fields")
        criterion = item["criterion_id"]
        if not isinstance(criterion, str) or criterion not in criterion_ids or criterion in seen:
            raise ValueError("Unknown or duplicate assessment criterion")
        seen.add(criterion)
        completeness, label = item["completeness"], item["expected_label"]
        if not isinstance(completeness, str) or completeness not in COMPLETENESS:
            raise ValueError("Unknown assessment completeness")
        if label is not None and (not isinstance(label, str) or label not in LABELS):
            raise ValueError("Expected label must be null or a registered evidence label")
        reviewers = item["adjudicated_by"]
        if not isinstance(reviewers, list) or any(not _text(r) for r in reviewers):
            raise ValueError("adjudicated_by must be a list of reviewer identifiers")
        if len({r.strip().casefold() for r in reviewers}) != len(reviewers):
            raise ValueError("Reviewer identifiers must be distinct")
        agreement = item["agreement"]
        if agreement is not None and (not isinstance(agreement, str) or agreement not in AGREEMENTS):
            raise ValueError("Unknown adjudication agreement")
        stamp = item["adjudicated_at"]
        if stamp is not None:
            _adjudication_time(stamp)
        if not isinstance(item["note"], str):
            raise ValueError("Assessment note must be a string")
        if label is not None and (not reviewers or stamp is None or agreement is None):
            raise ValueError("An adjudicated label requires reviewers, date and agreement")
        if label is not None and ((agreement == "single_reviewer" and len(reviewers) != 1)
                                  or (agreement != "single_reviewer" and len(reviewers) < 2)):
            raise ValueError("Agreement must describe the recorded reviewer count")
        codes = []
        if completeness != "adequate" and label not in (None, "insufficient_evidence"):
            codes.append("completeness_label_mismatch")
        has_observations = any(e["criterion_id"] == criterion for e in dossier["evidence"])
        if completeness == "absent" and has_observations:
            codes.append("absent_with_observations")
        elif completeness != "absent" and not has_observations:
            codes.append("non_absent_without_observations")
        flags.extend({"estate_id": dossier["estate_id"], "criterion_id": criterion, "code": code} for code in codes)
    if seen != set(criterion_ids):
        raise ValueError("Exactly one analyst assessment is required per rubric criterion")
    return sorted(flags, key=lambda f: (f["estate_id"], f["criterion_id"], f["code"]))


def check_reference_ready(rows, criterion_ids, *, first_run_at):
    """Fail closed on pending/late labels. Does not score or change any label."""
    first = _timestamp(first_run_at)
    if not rows or not criterion_ids:
        raise ValueError("Reference check needs dossiers and rubric criteria")
    flags, seen, count = [], set(), 0
    for dossier in sorted(rows, key=lambda r: r["estate_id"]):
        if dossier["estate_id"] in seen:
            raise ValueError("Duplicate estate_id in reference records")
        seen.add(dossier["estate_id"])
        flags.extend(validate_assessments(dossier, criterion_ids))
        for item in dossier["analyst_assessments"]:
            if item["expected_label"] is None:
                raise ValueError("Reference label not adjudicated; reference scoring is blocked")
            if _adjudication_time(item["adjudicated_at"]) >= first:
                raise ValueError("Every adjudication must precede the first Jev run")
            count += 1
    return {"status": "adjudicated_with_review_flags" if flags else "adjudicated",
            "assessment_count": count, "first_run_at": first.isoformat(), "review_flags": flags,
            "interpretation": "Schema and declared timing checks only; not proof of expert correctness or run history. Flags require human review and never change labels."}
