# Build status

Version 0.2.0 is under local review. The standard-library offline core runs
from a checkout on Python 3.11+. No live Jev calls or real estate ratings have
been produced. Hosted CI and installed-wheel packaging have not been verified.
Use `python3 -m unittest discover -s tests -v` to run the full suite.
Local verification on Python 3.14: 30 tests passed. The revised demo produced
20 trials and 80 simulated judgments with zero API calls; JSONL reanalysis
and compilation succeeded. Its original six-row export matched the hash below.

The original source is frozen at [v0.1.0](https://github.com/woodywu-sommelier/wine-judgment-lab/releases/tag/v0.1.0).
The original dataset is frozen at
[73ec2e6](https://huggingface.co/datasets/woodywu-sommelier/wine-judgment-lab-synthetic/tree/73ec2e61a28e7075c746c8ea573342a7613429af).
Its six-row file is retained unchanged in the v0.2 export; revised rows use a
separate config. See [changelog](../CHANGELOG.md) and [protocol](protocol.md).

Original HF file SHA-256 values (unchanged):

- `README.md`: `c0d1ce1d3572499222c08ea16387020c138e991faf51a4ab0dbd229e539f8a89`
- `data/trials.jsonl`: `8db5a7b7ddb76d1f0e2d5f7e278c57aed70aeceedaf4345b605b9049d3d6d125`

The README hash refers to the original fixed commit, not a later dataset card
with a v0.2 changelog. Real-data feasibility, immutable preregistration,
provider integration, ordinal regression and expert review remain future work.
