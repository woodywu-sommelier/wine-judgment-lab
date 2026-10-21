# First real dossiers: feasibility ledger

Prepare 3–5 estates before choosing the full pilot size. Include at least one
grower with sparse documentation, and cover selection/tier differences rather
than only famous names. Fix the edition, region, candidate pool and selection
rationale before collection. This is a feasibility exercise, not a representative
quality ranking or a model-performance study. No model calls are needed.

Keep actual records under ignored `local/`, owner-only. Public documentation
contains this specification only, not private reviewer identities or source notes.
The ledger is separate from the validated model-input and information-audit
schemas; it is not silently accepted as training data.

## Estate and selection record

Record estate ID, real name, region, selected edition, collector, dates and
why this estate was included. Store `selection_status` as `listed`,
`not_listed` or `unknown`; `grape_tier` as `Selected`, `1`, `2`, `3` or null.
`not_listed` and `unknown` have null tier, not an invented zero quality score.
Record the official selection source, retrieval date and search scope.
Declare `not_listed` only after checking the complete relevant edition, not
because one search returned nothing. In the later information audit, Selected
maps to tier 0; not-listed estates are outside that audit's selected-only frame.

## Time by phase

Use actual elapsed minutes per estate, with start/stop records or a stated
retrospective estimate. Keep unknown time null, not zero. Record overlapping
work and shared research separately so totals do not double-count it.

| Phase | Include |
| --- | --- |
| Searching | Finding candidate sources, including unsuccessful searches |
| Reading | Reading and checking the accessible material |
| Structuring | Extracting permitted facts and constructing criterion evidence |
| Rights check | Determining access, reuse and redistribution conditions |
| Leak review | Writing aliases; automatic and human identity checks |

Also record adjudication time separately if performed; do not hide it inside
structuring or claim this exercise measures an inspector's entire workload.

## Source ledger

For every source found, retain source ID, title/publisher, URL/archive URL,
retrieval and evidence dates, access status (`accessible`, `paywalled`,
`unusable`, or `not_checked`), and why unusable where applicable. Log search
attempts with no usable source separately; absence of a found source is not
proof that no such evidence exists.

Record rights status and its basis for each source and extracted observation:
original, explicit permission, reusable license, link-only/facts-only pending
review, prohibited, or unknown. Record the applicable terms/license URL and
attribution requirements. Access does not imply redistribution permission.
Do not bypass paywalls, publish paid tasting notes, or copy private correspondence.
Keep inaccessible/unknown-rights sources in the ledger rather than silently
discarding them or presenting their contents as verified evidence.

## Identity and leakage

Preserve the reviewer-written producer/swap `name_aliases`, the manual
`identity_leakage` decision and reviewer/date, the automatic flag from generated
trials, and the effective OR flag. Record likely indirect clues (vineyards,
family names not on the alias list, distinctive descriptions) privately.
No automatic match is not proof of anonymity. Do not redact after seeing
model output. Follow the protocol's unchanged-text all/clean policy.

## Criterion coverage and adjudication

For each rubric criterion, record observation count and one
`analyst_assessments` entry: completeness (`absent`, `partial`, `conflicting`,
`adequate`), nullable expected label, reviewer IDs/date/agreement and note.
An absent criterion still requires a record. Keep provenance on observations.
Completeness describes the combined criterion evidence, not a judgment that
the estate is good or bad. Keep unadjudicated labels null; never derive them
automatically from completeness or from a model response.

## Feasibility report before scaling

Report per-estate phase times and total preparation time; sources found and
access/rights breakdown; alias and leak flags; counts/shares of each completeness
state by criterion; and the selected tier/status coverage. Report missing
times, unusable sources and pending adjudications explicitly.

Identify the sparsely documented grower in the private report and explain
its selection. Compare its preparation cost and evidence insufficiency with
the rest without treating missing documentation as inferior wine. Retain it
when estimating workload; do not drop it to make model coverage look better.
With 3–5 estates, describe observations only—no population-level claims.

Use these results to freeze a feasible pilot sample, budget and evidence
collection rules, then finalize and register the exact protocol commit before
the first Jev request. Do not create a protocol tag that implies registration
while these decisions are still open.
