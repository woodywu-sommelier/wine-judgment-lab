# Changelog

## 0.2.0 — local review, 2026-10-20

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
The readable HF tag is pending authenticated access; the fixed commit is the
reproduction reference. Never force-push or squash this dataset's history.

Two fictional dossiers, six trials, twelve simulated judgments, 21 tests.
Known limitations motivated v0.2: judge-visible verification tags, no repeat
variability comparator, no neutral condition/transitions, manual-only leak
flags, and an unstratified regional split. Reproduce using the frozen code,
not the current CLI.
