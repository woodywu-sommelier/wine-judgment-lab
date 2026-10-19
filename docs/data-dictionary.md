# Input and result contracts

JSON inputs reject duplicate object keys and nonfinite numeric constants.

## Dossier JSON array

Each dossier needs `estate_id`, `producer_name`, `swap_name`, `region`, boolean
`synthetic`, boolean `identity_leakage`, boolean `swap_plausible`, `evidence`
and `sources`. Use stable estate IDs and distinct displayed original/swap names.

Each evidence object needs `criterion_id`, `observation`, `verification`
(`independent`, `producer_claim`, or `missing`) and an existing `source_id`.
Each source needs `source_id`, `url`, `rights`. Production dossiers should also
record retrieval time, observation date, original-vs-secondary provenance and
access limitations. The current validator checks structural completeness, not
the truth or legal status of a source. `evidence: []` is allowed.

Identity-leakage and swap-plausibility decisions are recorded by a reviewer
before the run, not inferred from model outcomes. Explicit source IDs and URLs
stay in dossiers and are omitted from judge-facing observations.

## Rubric JSON

`version` plus nonempty `questions` with unique `criterion_id`, `instructions`
and a `labels` map defining `supported`, `contradicted`, `insufficient_evidence`.
These evidence categories are nominal, not an ordered wine-quality scale.

## Trials and judgments JSONL

The prepare command emits one trial per estate/condition. SHA-256 fields bind
canonical observations, rubric and complete trial. One JSON object per line.

Each imported judgment needs `trial_id`, `trial_hash`, `criterion_id`, `label`,
`provider`, `model`, `run_id`, integer `repeat_id` and timezone-aware ISO
`created_at`. One invocation analyzes one provider/model. Every run/repeat must
contain exactly one judgment for every trial/question. Do not change the model
behind a fixed model identifier or combine model versions. Record actual API
receipts and errors in separate files before constructing complete result sets.

Summary rates pool complete pairs descriptively. They are not confidence
intervals, hypothesis tests or independent-estate counts. Different repeats
of the same estate remain dependent. The clean subset excludes identity leaks;
the swap subset excludes reviewer-marked implausible pairings.

## Information-audit JSON array

One aggregated row per estate: `estate_id`, `region`, integer `tier` (0 Selected,
1, 2 or 3), `reference_price` or null, ISO date `price_observed_at` or null,
`award_published_at`, `critic_coverage` (`found`, `searched_not_found`,
`not_searched`) and boolean `synthetic`.

A present price must be finite, positive and observed strictly before the
announcement. A missing price stays null. The validator does not certify that
the dates are genuine or the wines comparable. For real collection, preserve
wine, vintage, 750 ml size, currency, tax basis, merchant, archive URL, retrieval
date, search scope and redistribution status in a separate source ledger.

The current baseline does not use price or critic information to predict tiers.
It establishes a training-only comparison for a later ordinal model. Split
membership is hash-based on seed, region and estate ID, not award tier or input
order. Test share is floor(n/4), at least one; tiny regions with fewer than two
estates fail. Macro-F1 averages labels present in truth or predictions, as named
in its output. Always report regional class/sample counts; tiny demos do not
establish predictive performance.
