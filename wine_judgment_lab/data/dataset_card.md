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
---

# Wine Judgment Lab — Synthetic Identity Trials

Created by Woody Wu. Version 0.1.0. All six trial rows are fictional software
examples derived from two original fictional dossiers. No model was called to
create labels. This release contains no ratings of real estates and no measured
Jev performance. It is a method demonstration, not a trained model.

Code and research protocol:
https://github.com/woodywu-sommelier/wine-judgment-lab.

## Purpose

Explore whether a displayed producer identity can change a rubric judgment
while the substantive evidence remains fixed. Each fictional dossier has named,
anonymous and swapped-name variants. These names carry no validated prestige
difference; synthetic results cannot establish reputation bias.

## Fields

`trial_id` identifies a variant; `estate_id` groups all variants of a dossier;
`condition` is named, anonymous or swapped; `synthetic` is true. `state_json`
contains the exact potential judge input; `questions_json` contains the rubric.
`evidence_hash`, `rubric_hash` and `trial_hash` preserve provenance. The leakage
and swap-plausibility booleans are explicit fixture assumptions, not an audit
of real-world anonymity. Hashes use canonical UTF-8 JSON with sorted keys.

## Creation and reuse

Reproduce with `python3 -m wine_judgment_lab demo --out runs/demo` from the
GitHub code project. The generated `huggingface/` folder is a standalone dataset
repository export. Keep all three variants of an estate in the same split if
you later create train/test partitions. The `example` split is intentionally
not labeled a research test set. Do not train on it and claim independent
evaluation on its sibling variants.

Original synthetic examples are CC BY 4.0; attribute Woody Wu and Wine Judgment
Lab. Code is separately MIT licensed. Source URLs under example.org are
fictional provenance illustrations, not fetched evidence. Third-party wine
notes, merchant data and Michelin content are absent. Their rights do not
transfer through this license.

## Limitations

Two fictional dossiers cannot establish model fairness, sensory ability,
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
