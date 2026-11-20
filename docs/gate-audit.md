# Sufficiency-gate audit

A ranking that only scores entries whose evidence is "sufficient" makes two
decisions: how it scores the evidence, and whose evidence it accepts as enough.
The second decision decides who appears in the ranking at all. This audit
measures it across identity conditions, cutoffs and repeats.

Origin: an exploratory, one-run-per-condition test on a published restaurant
industry list found that showing names barely moved scores but changed who
cleared a 0.70 sufficiency cutoff. That run is not reproduced here; it is
private and exploratory. This module makes the same question testable with
repeats in any study, including the Burgundy pilot.

## Input

`gate --judgments FILE` reads JSONL, one object per entity, condition and
repeat:

| Field | Type | Meaning |
|---|---|---|
| `entity_id` | string | Stable private ID (a person, estate or venue) |
| `condition` | string | e.g. `named`, `masked`, `neutral` |
| `run_id`, `repeat_id` | string, integer ≥ 0 | Repeats are `(run_id, repeat_id)` pairs |
| `score` | finite number | The ranking score |
| `sufficiency` | number in [0, 1] | The model's evidence-sufficiency estimate |
| `provider`, `model` | string | One judge per analysis |
| `synthetic` | boolean | Explicit |

Every entity needs every condition in every repeat. At least two repeats are
required; `--allow-single-repeat` accepts one and labels the output
`exploratory_single_repeat`.

Optional: `--leaks` (entity → true if the dossier reveals identity) adds a
clean-subset analysis; `--external-ranks` (entity → rank, 1 = best, e.g. a
peer vote) adds Spearman agreement oriented so positive means agreement.

## Output, per population (all, and clean when leaks are given)

- **Qualification by cutoff** (default 0.60 to 0.80): how many qualify in each
  condition, how many qualify only under the reference condition or only
  under the comparison, and how many reference medians sit within the
  near-cutoff band (default ±0.03). Flips are only informative beside that
  count: a small shift moves many entries when many sit near the line.
- **Gate noise**: entities whose qualification changes between repeats of the
  same condition. Compare this with flips between conditions before calling
  anything a name effect. With a single repeat it is `null` (not measured),
  never zero.
- **Sufficiency shift**: median change, counts down, up and unchanged, and an
  exact two-sided sign test (descriptive; p-values to three significant
  figures).
- **Scores**: Spearman across all entities and median absolute shift.
- **Leaders** with and without each cutoff.

An entity qualifies when its **median** sufficiency across repeats is at or
above the cutoff.

## Reading it

- A difference in who qualifies is a finding only when it exceeds repeat
  instability at the same cutoff.
- A neutral invented name separates "a famous name helps" from "a missing
  name makes the model cautious".
- Masked dossiers can still reveal identity; report all and clean results.
- None of this measures quality or establishes causal prestige bias.

## Publication

Output contains private entity IDs and leaders. Publish aggregates only:
counts by cutoff, shift summaries, correlations and repeat noise. Do not
publish per-person or per-estate scores or rankings of real people or
producers, dossier source text, or a third party's full list. Check the
model provider's terms on publishing evaluation results before release.
