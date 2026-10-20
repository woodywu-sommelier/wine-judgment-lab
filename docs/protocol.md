# Wine Judgment Lab: exploratory protocol, version 0.2

Author: Woody Wu. Prepared 2026-10-19; amended 2026-10-20 before any real inference.

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
Split by estate, stratified within region and tier; all wines and vintages from
one estate stay together. Within each stratum of at least two estates, hold out
max(1, floor(n/4)), leaving the rest for training. Singletons remain in training.
Report all four tiers' train/test counts. A tier with no held-out estates is
`not_evaluable`, with null metrics; never quietly drop it or report a score.
If a region has no held-out estates, its aggregate score is also null.
Stratification uses labels to define membership, not to fit the predictor.
Freeze the resulting split before fitting; do not retune it using results. Analyze
regions separately. Learn scaling/imputation on training estates only. Compare
an ordinal model with the training-only modal baseline. The initial software
implements the baseline and held-out metrics; ordinal fitting is a later phase.
Do not use holdout results to select predictors or thresholds. Report macro-F1,
accuracy, mean absolute tier error and sample counts. With sparse classes,
report uncertainty and fold composition rather than declaring a winner.
Cross-region transfer is exploratory until feature definitions are comparable.

## Experiment B: identity sensitivity

Use sourced, structured dossiers with separate human-reviewed factual evidence.
Freeze the rubric and model version. Four variants differ only in the
displayed identity: named, anonymous, neutral invented name and swapped.
Neutral is a comparison cue, not a zero-identity baseline. It may carry its own
associations. The core does not send source
URLs or canonical estate IDs to the judge. Actual evidence is identical across
variants and has a stored hash. Dossiers require an identity-leakage flag and a
plausibility decision for their swap. Vineyard details can reveal identity
even without the name; report the clean subset separately from all dossiers.
Analyst verification tags remain in a private local record, not judge inputs.
Every dossier requires an explicit reviewer-written `name_aliases` list for
short forms of the producer and swapped name. Keep this list in the private
record, not judge inputs. Literal producer/swap names and listed aliases in
observation text are flagged automatically
(case-insensitive, word-boundary matching); the effective leak flag is the OR
of this check and the human flag. This check does not replace human review of
vineyard names, unlisted aliases, source descriptions or other indirect identity clues.
Include ambiguous evidence and frozen insufficiency criteria rather than only
obvious supported/unsupported cases; synthetic ambiguity does not prove that
real-world inputs or a particular model will be difficult to assess.

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
criterion and dossier, reported beside same-trial repeated-run disagreement.
Require at least two complete repeats in each provider/model/run; two separate
single-repeat runs do not satisfy this requirement. Same-input variability
compares all pairs of repeats within a run, separately by condition as well as
pooled, with comparison and disagreement counts. Repeated pairs are dependent;
these summaries are not significance tests or noise-adjusted causal estimates.
Also report named/neutral and swapped/named disagreement, abstention rates,
and complete 3×3 tables with named labels as rows and each comparison's labels
as columns. Those tables show direction of label changes, not prestige bias:
a real name may carry real information. The swapped table and rate both use
only plausible swaps; anonymous/neutral
tables use all dossiers, with populations explicitly labeled.

For every measure, also report the `clean_subset`: exclude all dossiers flagged
by either automatic or human leakage checks. This includes named/neutral and
swapped/named disagreement, every transition table, same-input variability
pooled and by condition, and insufficient-evidence rates. Clean swapped
tables and rates use the intersection of clean and plausible-swap dossiers.
Report denominators; zero eligible dossiers means null rates and zero counts,
not evidence of invariance. Validate complete repeats on all inputs before
constructing either population.

Use equal repeat counts across real-study runs: otherwise pooled condition rates
weight runs linearly in repeats, but repeat-noise rates weight them by the
number of repeat pairs. Neither pooled metric is a causal correction.
A signed quality effect requires a separately
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
