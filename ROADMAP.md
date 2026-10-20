# Roadmap

## 0.1 — offline starter

- [x] Research protocol and explicit claim boundaries.
- [x] Fictional evidence dossiers and a versioned atomic rubric.
- [x] Deterministic named/anonymous/swapped trials and input hashes.
- [x] Complete paired-judgment validation and descriptive analysis.
- [x] Region-specific train/test baseline with historical-price cutoff checks.
- [x] CLI, tests, manual-install CI example, dataset card and HF export.

## 0.2 — published method revisions

- [x] Private analyst tags, four identity conditions and ambiguous fictional dossiers.
- [x] Mandatory repeats, same-input variability and 3×3 transition tables.
- [x] Automatic literal-name leakage flags alongside human review.
- [x] Region/tier-stratified splits with explicit per-tier evaluability.
- [x] Versioned HF export preserving original six rows and adding `v0.2`.
- [x] Shorten public working notes; keep detailed records locally.
- [x] Review and publish revised software and dataset config.
- [x] Create the readable HF `v0.1.0` tag at the original dataset commit.

### Review follow-ups (not pilot blockers)

- [ ] Distinguish absent evidence from partial/conflicting evidence in private analyst records.
- [ ] Restore held-out-label invariance coverage using an explicit frozen split at fitting time.
- [ ] Copy frozen v0.1 export bytes directly rather than re-encoding parsed JSON.

## Next — data feasibility and registered pilot

- [x] Confirm `woodywu-sommelier` as the owner on both services.
- [x] Publish and verify the GitHub starter from a fresh public clone.
- [x] Publish the synthetic Hugging Face dataset and verify its six-row viewer.
- [ ] Obtain a small real sample with comparable historical prices and a source ledger.
- [ ] Define blind evidence review, sampling and swap-pairing process.
- [ ] Finalize endpoints, model comparison, repeats, sample size and analysis.
- [ ] Register the protocol immutably before real model inference.
- [ ] Build a pinned/versioned Jev adapter with request manifests, usage receipts,
  recoverable logs, retry accounting and a strict approved spending limit.
- [ ] Add training-only imputation and an ordinal model with regional held-out
  evaluation and uncertainty; the modal baseline remains the reference.
- [ ] Run the pilot and publish reviewed permitted data and negative findings.

## Later, if evidence justifies it

- [ ] Compare expert-only, model-only and expert-assisted judgments.
- [ ] Investigate buyer utility using independently defined outcomes.
- [ ] Add an HF demonstration Space after an interpretable result exists.

Every phase depends on the preceding evidence. No global estate ranking is planned
for the starter.
