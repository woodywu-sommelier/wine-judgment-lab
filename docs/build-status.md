# Build status — 2026-10-19

Local version 0.1.0 created in a new Wine Judgment Lab folder. No existing bot,
brief-engine project or live database was changed.

Verification on Python 3.14:

```text
python3 -m unittest discover -s tests -v
Ran 21 tests
OK
```

`python3 -m compileall -q wine_judgment_lab` completed successfully.
The demo created six fictional trials and twelve simulated judgments with
`api_calls: 0`. Reanalysis of the exported JSONL completed successfully.
The generated Hugging Face folder has a metadata card and six JSONL trial rows.
Source examples contain no real producer assessments. The source credential
pattern check found no credential matches.

Not verified here: installed-wheel packaging (setuptools is absent), remote
GitHub Actions, Hugging Face publication, real data acquisition, a Jev adapter,
ordinal regression or any empirical claim. The package runs directly from its
checkout with only the Python standard library. The `gh` and `hf` commands are
not available on this shell. Kendall confirmed `woodywu-sommelier` for both
accounts. The saved GitHub credential verified that identity and created
https://github.com/woodywu-sommelier/wine-judgment-lab. Hugging Face has no
saved credential available; its sign-in page is prepared for the owner.

The first GitHub push was rejected because the saved token lacks the `workflow`
scope. The reviewed release retains CI as `docs/ci-tests.yml.example`; the
active `.github/workflows/tests.yml` copy is preserved locally and excluded from
the public commit. No permission was broadened and no remote history was overwritten.

Publication verified: the public GitHub source at commit `6e5e174` was cloned
into a fresh temporary directory and all 21 tests passed there (0.587 seconds).
The remote `main` ref matched that published commit. The source is public and
downloadable. Hosted CI remains inactive pending manual workflow installation.
The final HF upload folder is `runs/publication-demo/huggingface/`, regenerated
with the verified GitHub link. Hugging Face remains on its login page, so its
dataset has not been created or uploaded.

Next concrete step: complete Hugging Face login and dataset publication, then assemble a verified pilot dataset
and register the real study before any paid inference. The publication guide
and roadmap separate software demonstration from research findings.
