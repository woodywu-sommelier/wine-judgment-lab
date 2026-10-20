---
pretty_name: Wine Judgment Lab — Synthetic Identity Trials
language:
- en
license: cc-by-4.0
task_categories:
- text-classification
tags:
- wine
- evaluation
- synthetic
- identity-sensitivity
- rubric-evaluation
size_categories:
- n<1K
configs:
- config_name: synthetic_trials
  data_files:
  - split: example
    path: data/trials.jsonl
- config_name: v0.2
  data_files:
  - split: example
    path: data/v0.2/trials.jsonl
---

# Wine Judgment Lab — Synthetic Identity Trials

Created by Woody Wu. This export preserves the original six-row
`synthetic_trials` config and adds the separate `v0.2` config: twenty trials
from five fictional dossiers. No model was called to create labels. Neither
config contains ratings of real estates or measured Jev performance.
This is a method demonstration, not a trained model.

## Changelog and frozen v0.1

- v0.1.0: six original named/anonymous/swapped trials. Frozen dataset commit:
  [73ec2e6](https://huggingface.co/datasets/woodywu-sommelier/wine-judgment-lab-synthetic/tree/73ec2e61a28e7075c746c8ea573342a7613429af).
  Frozen code: [v0.1.0](https://github.com/woodywu-sommelier/wine-judgment-lab/releases/tag/v0.1.0).
  `data/trials.jsonl` is preserved byte for byte. Its analyst verification tags
  are a known v0.1 design limitation; use that config only to reproduce v0.1.
- v0.2.0: four identity conditions, including a neutral invented-name
  comparison; three new ambiguous fictional dossiers; analyst verification
  tags removed from judge inputs; separate manual/automatic literal-name leak
  flags. The code requires two or more repeats per run and reports same-input
  variability beside condition disagreement and full 3×3 transition counts.
  Revised rows live only in `data/v0.2/trials.jsonl`.

Code and research protocol:
https://github.com/woodywu-sommelier/wine-judgment-lab.

## Purpose

Explore whether a displayed producer identity can change a rubric judgment
while the substantive evidence remains fixed. Revised dossiers have named,
anonymous, neutral and swapped-name variants. These names carry no validated prestige
difference; synthetic results cannot establish reputation bias. A neutral name
is a comparison cue, not a zero-identity baseline. Transition counts describe
directions of label changes, not causal prestige bias: real names may carry
real information.

## Fields

`trial_id` identifies a variant; `estate_id` groups all variants of a dossier;
`condition` is named, anonymous, neutral or swapped in v0.2; `synthetic` is true. `state_json`
contains the exact potential judge input; `questions_json` contains the rubric.
`evidence_hash`, `rubric_hash` and `trial_hash` preserve provenance. The leakage
and swap-plausibility booleans are explicit fixture assumptions, not an audit
of real-world anonymity. v0.2 adds manual and automatic leakage flags; the
effective flag is their logical OR. Literal detection cannot find all indirect
identity clues. Analyst records are excluded from the HF export.
Hashes use canonical UTF-8 JSON with sorted keys.

## Creation and reuse

Reproduce with `python3 -m wine_judgment_lab demo --out runs/demo` from the
GitHub code project. The generated `huggingface/` folder is a standalone dataset
repository export. Keep all variants of an estate in the same split if
you later create train/test partitions. The `example` split is intentionally
not labeled a research test set. Do not train on it and claim independent
evaluation on its sibling variants.

Original synthetic examples are CC BY 4.0; attribute Woody Wu and Wine Judgment
Lab. Code is separately MIT licensed. Source URLs under example.org are
fictional provenance illustrations, not fetched evidence. Third-party wine
notes, merchant data and Michelin content are absent. Their rights do not
transfer through this license.

## Limitations

These fictional dossiers cannot establish model fairness, sensory ability,
objective wine quality, producer quality or superiority over Michelin. The
rubric assesses whether supplied observations support claims. It cannot verify
an observation against the physical vineyard or wine. Swapped real names would
require separate ethical/editorial review, plausibility checks and clear
experimental labeling. No real-world or confirmatory results exist yet.

## Intended publication relationship

GitHub carries software, protocol and tests. This Hugging Face dataset export
carries permitted examples and their card. A future real dataset needs sourced
facts, cutoff dates, redistribution review, frozen study decisions and complete
model/run metadata before its results can be interpreted.
