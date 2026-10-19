# Wine Judgment Lab: exploratory protocol, version 0.1

Author: Woody Wu. Prepared 2026-10-19.

Status: draft protocol and offline software demonstration. This file is not a
preregistration and no real-estate experiment has been run. Publish an immutable
registration with a trusted timestamp before the confirmatory run. Changes
after registration require a dated amendment; exploratory analyses stay labeled.

## Questions and claim boundaries

A. How predictable are distinctions within a published Michelin wine-estate
selection from information available before its announcement?

B. Does a producer identity cue change a model's evidence assessment when the
substantive dossier and rubric remain identical?

A measures predictability, not wine quality, causal prestige bias, or buyer
utility. B measures identity sensitivity, not sensory ability or superiority
over inspectors. Neither uses Michelin's unpublished inspection evidence.
The model's confidence is not proof, and human agreement is not absolute truth.

## Initial release

The public starter contains fictional estates and original synthetic evidence
only. Its outputs demonstrate software behavior, not findings about Michelin,
real producers, or Jev. The core has no networking or API-key access. A provider
adapter and a real-data collection step require their own validated extension.

## Experiment A: information audit

Collect estates within one frozen edition. Preserve region, exact award tier,
source, retrieval time and announcement cutoff. Do not interpret absence from
the list as an adverse judgment. The initial population includes selected
estates only; any study of omissions needs a separate sampling frame.

Each price observation must identify bottling, vintage, size, currency, tax
basis, merchant, observation date, archive URL and redistribution status. Use a
regional wine-sampling rule: a village-level Burgundy wine cannot serve as a
universal Bordeaux estate proxy. Record exclusions and unavailable histories.
No post-announcement price is eligible for the pre-award analysis. Do not
silently replace historical observations with current prices or proxy dates.

Critic evidence means coverage found in named sources by a cutoff date, not
universal proof that coverage exists or is absent. Separate coverage missing,
coverage searched and not found, and coverage found. Track source access cost.

Fix predictors, grouping, random seed and missing-data strategy before fitting.
Split by estate; all wines and vintages from one estate stay together. Analyze
regions separately. Learn scaling/imputation on training estates only. Compare
an ordinal model with the training-only modal baseline. The initial software
implements the baseline and held-out metrics; ordinal fitting is a later phase.
Do not use holdout results to select predictors or thresholds. Report macro-F1,
accuracy, mean absolute tier error and sample counts. With sparse classes,
report uncertainty and fold composition rather than declaring a winner.
Cross-region transfer is exploratory until feature definitions are comparable.

## Experiment B: identity sensitivity

Use sourced, structured dossiers with separate human-reviewed factual evidence.
Freeze the rubric and model version. Three variants differ only in the
displayed identity: named, anonymous and swapped. The core does not send source
URLs or canonical estate IDs to the judge. Actual evidence is identical across
variants and has a stored hash. Dossiers require an identity-leakage flag and a
plausibility decision for their swap. Vineyard details can reveal identity
even without the name; report the clean subset separately from all dossiers.

For real data, make swaps within compatible regional and production contexts.
A contradiction discovered through a name mismatch is not evidence of prestige
bias. Predesign pairings independently of model outcomes. Do not publish a
fabricated claim attached to a real producer without conspicuous experimental
labeling and careful review. Public synthetic fixtures use fictional names.

Ask atomic evidence questions: independently supported, contradicted, or
insufficient evidence. These labels are not wine scores. Missing documentation
is not a negative finding. Keep the same questions and evidence for each
variant. A model can be very confident while wrong; confidence cannot override
known input insufficiency or replace an independent evidence audit.

Primary descriptive endpoint: paired named/anonymous label disagreement by
criterion and dossier. Secondary: swapped/named disagreement, abstention rates,
and repeated-run disagreement. A signed quality effect requires a separately
registered ordered quality scale; do not assign ordinal values to these three
evidence labels. Analyze repeated observations at estate level rather than
treating each criterion/call as an independent estate. Select the pilot size
for feasibility; choose a confirmatory size after a power analysis.

Every imported judgment must bind trial ID, trial hash, criterion ID, model,
provider, run ID, timestamp and repeat ID. Reject missing variants, mismatched
models, duplicate judgments and altered inputs. Log failures separately. API
latency/cost need provider usage receipts; do not compare them with an entire
human inspection budget. Collect preparation, verification and panel time too.

## Publication

GitHub holds original code, tests, method, amendments and reproducible commands.
Hugging Face holds a dataset card, permitted data and exact split definitions;
this is a dataset/method release, not a trained Jev model. The starter's
synthetic evidence may be redistributed under CC BY 4.0. Real data needs a
row-level rights review before upload. Never publish keys, paid tasting notes,
private correspondence or research participant identities by default.

Woody Wu's website hosts the permanent explanation and disclosures; Substack
hosts the reporting; LinkedIn gets one finding with methods linked in a comment.
Reddit contributions are native and link-free. Identify professional interests,
paid access, sponsorship, and relevant hospitality affiliations in the final
research report. Seek Michelin and estate responses before contested reporting.
