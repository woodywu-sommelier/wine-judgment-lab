# Wine Judgment Lab

**Can we make wine assessment more transparent—and test how much reputation influences AI judgment?**

An open research project by **Woody Wu**, hospitality operator, sommelier and
builder of The House Somm. Two experiments connect wine expertise with
reproducible model evaluation:

1. **What does the Grape rating add?** Study how predictable a published
   Michelin wine-estate tier is from information available before the award.
2. **Does the name change the judgment?** Compare identical evidence under
   named, anonymous, neutral invented-name and swapped producer identities.

## Current status

Version 0.2 is a published **offline research starter**; reviewed source is tagged
[v0.2.0](https://github.com/woodywu-sommelier/wine-judgment-lab/tree/v0.2.0).
The public v0.1 release remains frozen at [v0.1.0](https://github.com/woodywu-sommelier/wine-judgment-lab/releases/tag/v0.1.0).
The starter contains fictional estates,
original synthetic observations and simulated judgments. No real estate has
been scored, no Jev call has run, no public dataset has been scraped, and there
are no empirical findings about Michelin or model objectivity.

Implemented: validated dossier inputs, deterministic identity variants, frozen
input hashes, mandatory repeats, same-input variability, categorical transition
tables, literal-name leakage flags, leakage/plausibility subsets, region/tier-
stratified held-out modal baselines, CLI, tests and versioned Hugging Face export.
CI is supplied as [a manual-install workflow example](docs/ci-tests.yml.example);
hosted CI has not run.

Next: real-data feasibility, finalized preregistration, budgeted Jev adapter,
ordinal model, expert evidence review and pilot. [Protocol](docs/protocol.md)
explains each limitation and the planned research. An ordinal model is not
implemented in this starter. No trained model weights are distributed.

## Run it

Python 3.11 or newer. No installation or external packages are needed from a
checkout:

```bash
python3 -m unittest discover -s tests -v
python3 -m wine_judgment_lab demo --out runs/demo
```

The v0.2 demo creates twenty trials from five fictional estates, eighty
**simulated** judgments (two repeats and two criteria), an analysis summary,
a fictional held-out baseline, a manifest and a Hugging Face dataset folder.
The export retains the original six rows and adds a separate `v0.2` config.
All output paths refuse overwrite. `analyst_records.json` retains private
verification tags locally with owner-only permissions; it is not exported.

Recompute its results:

```bash
python3 -m wine_judgment_lab analyze \
  --trials runs/demo/trials.jsonl \
  --judgments runs/demo/simulated_judgments.jsonl \
  --out runs/recomputed-summary.json
```

Prepare your own input using the examples under `wine_judgment_lab/data/`:

```bash
python3 -m wine_judgment_lab prepare \
  --dossiers wine_judgment_lab/data/dossiers.json \
  --rubric wine_judgment_lab/data/rubric.json \
  --seed 19 --out runs/prepared

python3 -m wine_judgment_lab audit \
  --rows wine_judgment_lab/data/audit.json \
  --seed 19 --out runs/baseline.json
```

The four conditions are named, anonymous, neutral invented name, and swapped.
Neutral is a comparison cue, not a zero-identity baseline. `analyze` requires
at least two complete repeats within every run. Its transition tables count
label changes, not causal prestige bias or wine-quality gains.

`prepare` never constructs a model client. Only the trial's `state` and
`questions` are candidate judge inputs: estate IDs, source URLs, conditions and
analyst metadata must not be sent to a judge by a future adapter. Keep source
provenance locally for independent verification. A future live adapter must
report actual provider/model version, token use, cost and failures with a
preapproved spending cap.

## Why this exists

Wine assessment combines sensory observations, evidence, judgment and
reputation. Software can expose a rubric and preserve inputs, but it cannot
create independent observations of a vineyard or taste wine. We want to test
which parts become more consistent, inspectable and useful—not assume that
AI is objective or that an established institution is wrong.

An identity-sensitive model is not automatically prestige-biased: mismatched
identities can introduce contradictions. A predictable award is not automatically
redundant or biased: price and recognized quality may share causes. The study
will retain those distinctions and publish negative as well as positive results.

## Publication structure

- **GitHub:** original software, protocol, tests, amendments and reproducibility.
- **Hugging Face dataset:** [versioned fictional identity trials](https://huggingface.co/datasets/woodywu-sommelier/wine-judgment-lab-synthetic)
  with six preserved v0.1 examples and twenty in config `v0.2`, a dataset card,
  provenance hashes and `example` splits. These are software examples, not findings.
- **Permanent reporting:** [woodywusommelier.com](https://woodywusommelier.com),
  with the narrative edition in *The Floor and the Terminal*.

See [changelog](CHANGELOG.md), [publication steps](docs/publication.md), [data dictionary](docs/data-dictionary.md)
and [roadmap](ROADMAP.md). GitHub code lives at
[woodywu-sommelier/wine-judgment-lab](https://github.com/woodywu-sommelier/wine-judgment-lab).
The [Hugging Face dataset](https://huggingface.co/datasets/woodywu-sommelier/wine-judgment-lab-synthetic)
is also public and links back to this code and protocol.

## Contributing

Useful contributions: independently verifiable source suggestions, wine-sampling
rules, rubric critiques, test cases, statistical review and corrections. Open an
issue describing the question, evidence and limits. Do not upload keys, private
correspondence or copyrighted tasting notes. Keep real producer name swaps out
of public examples until reviewed. Replication and disagreement are welcome.

## References to investigate

- [Michelin's winery methodology](https://guide.michelin.com/gb/en/article/wine/the-michelin-guide-to-launch-its-first-wine-selection-in-burgundy-on-7-july-2026)
- [Michelin's Bordeaux selection](https://guide.michelin.com/us/en/article/wine/the-michelin-guide-s-bordeaux-wine-selection)
- [TypeSafe: structured decisions](https://docs.typesafe.ai/introduction)
- [TypeSafe: confidence](https://docs.typesafe.ai/confidence)
- [Decision Models vs. LLMs as Rubric Judges, v3](https://arxiv.org/abs/2609.29769v3)
- [Evaluating and Benchmarking the System One Model Jev](https://arxiv.org/abs/2609.37647)

These are background sources, not redistributed dataset contents. The project
is independently authored; it has no claimed endorsement from Michelin or
TypeSafe. Record sponsorship, paid access and professional interests in every
real study report. Expert review is planned; it has not yet occurred.

## Licenses

Code: [MIT](LICENSE). Original fictional data: [CC BY 4.0](DATA_LICENSE.md).
Neither license grants rights to third-party wine data or publications.
