# Publication and reporting

- [GitHub](https://github.com/woodywu-sommelier/wine-judgment-lab): software,
  protocol, tests and versioned changes; code is MIT licensed.
- [Hugging Face](https://huggingface.co/datasets/woodywu-sommelier/wine-judgment-lab-synthetic):
  original fictional examples and dataset card; data is CC BY 4.0.

## Versioned releases

Reproduce v0.1 using the [frozen source release](https://github.com/woodywu-sommelier/wine-judgment-lab/releases/tag/v0.1.0)
and [fixed dataset commit](https://huggingface.co/datasets/woodywu-sommelier/wine-judgment-lab-synthetic/tree/73ec2e61a28e7075c746c8ea573342a7613429af).
The [HF v0.1.0 tag](https://huggingface.co/datasets/woodywu-sommelier/wine-judgment-lab-synthetic/tree/v0.1.0)
also resolves to that fixed commit. Do not rewrite or squash history.

Reviewed v0.2 source is tagged
[v0.2.0](https://github.com/woodywu-sommelier/wine-judgment-lab/tree/v0.2.0).
The separate `v0.2` dataset config and changelog card were published at
[ba4d753](https://huggingface.co/datasets/woodywu-sommelier/wine-judgment-lab-synthetic/commit/ba4d753907058bc9adbc677be5a48663c0e643b6).
Public downloads match the local export; the original six-row file is unchanged.

Prepare a reviewed v0.2 export with:

```bash
python3 -m wine_judgment_lab demo --out runs/demo
```

The only public upload folder is `runs/demo/huggingface/`. Its card defines
two configs: original `synthetic_trials` pointing to `data/trials.jsonl`, and
revised `v0.2` pointing to `data/v0.2/trials.jsonl`. Preserve the original file
unchanged; upload the revised file and changelog card after review. Never upload
the parent run directory: it contains private `analyst_records.json`.
For real data, a row-level provenance and redistribution review is mandatory.

Local tests are required before publication. A manual-install CI template is
available at [ci-tests.yml.example](ci-tests.yml.example); hosted CI is not yet
active. No findings should be inferred from a synthetic demonstration.

## Research sequence

Review source feasibility and rights, freeze sampling and rubric decisions,
and register the protocol immutably before real inference. Log actual model
versions, usage, costs and errors; obtain independent expert review. Publish
limitations and negative findings alongside permitted data. Local commit
timestamps alone are not preregistration.

## Distinct publishing surfaces

- Website: permanent method, disclosures and source ledger alongside The House
  Somm and Service Audit, without claiming unmeasured product benefits.
- Substack: the reporting story in *The Floor and the Terminal*. Lead tags
  with Wine and Hospitality and use absolute links.
- LinkedIn: one native operator argument about auditability; method link in
  the first comment, no body link or hashtags.
- Reddit: native, link-free discussion of evidence requirements, not an essay repost.
- GitHub/HF: reproducible method, explicit limitations and contribution requests.

No launch copy should claim AI beats Michelin, is unbiased or can taste wine.
Real names can carry real information; transition counts describe label
changes, not causal prestige bias. Seek responses before contested reporting.
