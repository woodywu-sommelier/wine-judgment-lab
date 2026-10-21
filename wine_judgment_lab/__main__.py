"""Offline commands. No model clients, credentials, or network operations."""
import argparse
from datetime import datetime, UTC
import json
import os
from pathlib import Path
import sys

from . import __version__
from .audit import evaluate_baseline
from .analyst import validate_assessments, check_reference_ready
from .experiment import analyze, build_trials, digest

DATA = Path(__file__).with_name("data")


def _pairs(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError(f"Duplicate JSON key: {key}")
        out[key] = value
    return out


def _loads(text):
    def reject(value):
        raise ValueError(f"Nonfinite JSON value: {value}")
    return json.loads(text, object_pairs_hook=_pairs, parse_constant=reject)


def _json(path):
    return _loads(Path(path).read_text(encoding="utf-8"))


def _jsonl(path):
    return [_loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def _write(path, value, *, lines=False):
    text = ("".join(json.dumps(row, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n" for row in value)
            if lines else json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False, indent=2) + "\n")
    path = Path(path)
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        stream.write(text)


def _prepare(rows, rubric, seed, out):
    trials = build_trials(rows, rubric, seed=seed)
    out.mkdir(mode=0o700, parents=True, exist_ok=False)
    _write(out / "trials.jsonl", trials, lines=True)
    _write(out / "analyst_records.json", rows)
    criteria = {q["criterion_id"] for q in rubric["questions"]}
    _write(out / "analyst_review.json", {"review_flags": [f for row in rows for f in validate_assessments(row, criteria)]})
    _write(out / "manifest.json", {"version": __version__, "seed": seed, "dossiers_sha256": digest(rows),
           "rubric_sha256": digest(rubric), "trials_sha256": digest(trials), "trial_count": len(trials),
           "created_at": datetime.now(UTC).isoformat(), "api_calls": 0,
           "data_kind": "synthetic" if all(r["synthetic"] for r in rows) else "contains_real_data"})
    return trials


def _demo(out, seed):
    rows, rubric = _json(DATA / "dossiers.json"), _json(DATA / "rubric.json")
    trials = _prepare(rows, rubric, seed, out)
    judgments = []
    private = {r["estate_id"]: r for r in rows}
    for repeat in range(2):
        for trial in trials:
            for question in trial["questions"]:
                # Deliberate toy rule, not expert reference labels or empirical evidence.
                criterion = question["criterion_id"]
                assessment = next(a for a in private[trial["estate_id"]]["analyst_assessments"] if a["criterion_id"] == criterion)
                label = "supported" if assessment["completeness"] == "adequate" else "insufficient_evidence"
                judgments.append({"trial_id": trial["trial_id"], "trial_hash": trial["trial_hash"],
                     "criterion_id": criterion, "label": label, "provider": "simulated", "model": "synthetic-demo",
                     "run_id": "offline-demo", "repeat_id": repeat, "created_at": "2026-10-20T00:00:00Z"})
    _write(out / "simulated_judgments.jsonl", judgments, lines=True)
    _write(out / "summary.json", analyze(trials, judgments))
    _write(out / "audit_baseline.json", evaluate_baseline(_json(DATA / "audit.json"), seed=seed))
    hf = out / "huggingface"; (hf / "data" / "v0.2").mkdir(parents=True)
    (hf / "README.md").write_text((DATA / "dataset_card.md").read_text(encoding="utf-8"), encoding="utf-8")
    export = [{k: v for k, v in trial.items() if k not in {"state", "questions"}} | {
        "state_json": json.dumps(trial["state"], sort_keys=True, ensure_ascii=False),
        "questions_json": json.dumps(trial["questions"], sort_keys=True, ensure_ascii=False)} for trial in trials]
    _write(hf / "data" / "trials.jsonl", _jsonl(DATA / "v01-trials.jsonl"), lines=True)
    _write(hf / "data" / "v0.2" / "trials.jsonl", export, lines=True)
    return {"output": str(out), "data_kind": "synthetic", "api_calls": 0, "trials": len(trials), "judgments": len(judgments)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    demo = commands.add_parser("demo", help="write fictional demo and standalone Hugging Face dataset export")
    demo.add_argument("--out", type=Path, required=True); demo.add_argument("--seed", type=int, default=19)
    prepare = commands.add_parser("prepare", help="generate frozen variants from explicit dossiers and rubric")
    prepare.add_argument("--dossiers", required=True); prepare.add_argument("--rubric", required=True)
    prepare.add_argument("--out", type=Path, required=True); prepare.add_argument("--seed", type=int, default=19)
    analysis = commands.add_parser("analyze", help="validate imported results and summarize paired label changes")
    analysis.add_argument("--trials", required=True); analysis.add_argument("--judgments", required=True)
    analysis.add_argument("--out", type=Path, required=True)
    audit = commands.add_parser("audit", help="held-out training-only modal tier baseline")
    audit.add_argument("--rows", required=True); audit.add_argument("--out", type=Path, required=True)
    audit.add_argument("--seed", type=int, default=19)
    reference = commands.add_parser("check-reference", help="offline private adjudication/timing readiness check, not scoring")
    reference.add_argument("--dossiers", required=True); reference.add_argument("--rubric", required=True)
    reference.add_argument("--first-run-at", required=True); reference.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "demo":
            result = _demo(args.out, args.seed)
        elif args.command == "prepare":
            trials = _prepare(_json(args.dossiers), _json(args.rubric), args.seed, args.out)
            result = {"output": str(args.out), "trial_count": len(trials), "api_calls": 0}
        elif args.command == "analyze":
            result = analyze(_jsonl(args.trials), _jsonl(args.judgments)); _write(args.out, result)
        elif args.command == "check-reference":
            rows, rubric = _json(args.dossiers), _json(args.rubric)
            build_trials(rows, rubric, seed=0)  # full schema validation, no files or model client
            result = check_reference_ready(rows, {q["criterion_id"] for q in rubric["questions"]},
                                           first_run_at=args.first_run_at)
            _write(args.out, result)
        else:
            result = evaluate_baseline(_json(args.rows), seed=args.seed); _write(args.out, result)
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
