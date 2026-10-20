# Changelog

## Unreleased — 0.3.0.dev0

- Private criterion-level `analyst_assessments`, exactly one per rubric criterion,
  explicit completeness and nullable expected labels with adjudication metadata.
- Offline reference-readiness command: pending/late labels fail closed;
  mismatch flags require human review but never alter a label.
- Regression tests preserve all frozen trial fields across analyst edits and
  exclude assessment fields from trial/HF exports.
- Migrate ambiguous fictional records to partial/conflicting assessments and
  provenance-only item tags. The toy simulator reads completeness, not provenance
  or reference labels. Original v0.1 and v0.2 public trial bytes are unchanged.
- Feasibility-ledger instructions for 3–5 real estates; no real collection,
  inference, reference-agreement scoring or registration is included.

## 0.2.0 — published offline starter, 2026-10-20

Reviewed source tag: [v0.2.0](https://github.com/woodywu-sommelier/wine-judgment-lab/tree/v0.2.0).
Dataset commit: [ba4d753](https://huggingface.co/datasets/woodywu-sommelier/wine-judgment-lab-synthetic/tree/ba4d753907058bc9adbc677be5a48663c0e643b6).

- Judge observations omit analyst verification tags; prepare/demo preserve
  those tags in owner-only local analyst records, excluded from HF exports.
- Add a neutral invented-name comparison and three ambiguous fictional dossiers.
- Require at least two complete repeats within each model/run. Report
  same-input variability beside identity disagreement and full 3×3 transition
  counts. Direction of label changes is not evidence of causal prestige bias;
  a neutral name is a comparison point, not a zero-identity baseline.
- Combine automatic literal-name leak flags with manual review flags.
- Require reviewer-written name aliases (including producer/swap short forms)
  and match them without exposing the list to the judge. Report every metric
  for both all dossiers and a complete clean subset, with explicit denominators
  and clean/plausible intersections for swapped comparisons. Empty subsets
  return null rates; incomplete repeats fail before filtering.
- Stratify splits by region and tier. Keep singletons in training and report
  every tier with no held-out estates as not evaluable (null metrics).
- Export revised examples under config `v0.2`, path `data/v0.2/trials.jsonl`;
  preserve the original config and `data/trials.jsonl` byte for byte.
- Shorten public status/publication docs; retain working logs privately.

No real Jev inference, real estate ratings or confirmatory findings exist.

## 0.1.0 — frozen original demonstration

Code: [release v0.1.0](https://github.com/woodywu-sommelier/wine-judgment-lab/releases/tag/v0.1.0),
commit `6de068300bca3ed429baa0a55c3758523de3e482`.
Dataset: [original commit](https://huggingface.co/datasets/woodywu-sommelier/wine-judgment-lab-synthetic/tree/73ec2e61a28e7075c746c8ea573342a7613429af).
The readable [HF v0.1.0 tag](https://huggingface.co/datasets/woodywu-sommelier/wine-judgment-lab-synthetic/tree/v0.1.0)
resolves to that same fixed commit. Never force-push or squash this dataset's history.

Two fictional dossiers, six trials, twelve simulated judgments, 21 tests.
Known limitations motivated v0.2: judge-visible verification tags, no repeat
variability comparator, no neutral condition/transitions, manual-only leak
flags, and an unstratified regional split. Reproduce using the frozen code,
not the current CLI.
