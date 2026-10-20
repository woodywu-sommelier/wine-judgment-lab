# Publication and reporting plan

Owner confirmed by Kendall: `woodywu-sommelier` on both services.
GitHub repository created: https://github.com/woodywu-sommelier/wine-judgment-lab.
Hugging Face dataset published: https://huggingface.co/datasets/woodywu-sommelier/wine-judgment-lab-synthetic.

## GitHub

Repository: `woodywu-sommelier/wine-judgment-lab`, public.
Description: “Reproducible experiments on wine-assessment evidence,
producer identity and model judgment. Offline starter with synthetic examples.”

Before first push, review the exact file list. Keep `runs/`, credentials,
paid/private sources and all bot data excluded. Add only this project; do not
initialize or include the wallet bot or brief-engine. Initialize this new
project's own repository when publishing, commit the reviewed starter, and use
the account's ordinary authenticated GitHub publication workflow. Never put a
token in a URL or shell command. A local commit timestamp alone is not a
preregistration; use a trusted immutable registration before real inference.

GitHub CI note: the saved publishing token lacks the `workflow` scope. The
release therefore includes `docs/ci-tests.yml.example` rather than an active
Actions workflow. To enable it later, add that file as
`.github/workflows/tests.yml` using an account/session authorized to manage
workflows. The local workflow copy remains preserved, and local tests passed.

GitHub source publication is complete. A fresh clone of the public repository
passed all 21 tests. Hosted Actions has not run.

## Hugging Face

Dataset destination: `woodywu-sommelier/wine-judgment-lab-synthetic`, type
**dataset**. It is not a Jev model upload.

Run `python3 -m wine_judgment_lab demo --out runs/demo` once. The folder
`runs/demo/huggingface/` includes `README.md` with metadata and
`data/trials.jsonl` with six original fictional trials. Upload exactly that
folder through an authenticated HF dataset repository. The card specifies an
`example` split and states that no model call or real-world study occurred.
Link the final GitHub and HF URLs in both descriptions after they exist.

The published folder is `runs/publication-demo/huggingface/`; its card includes
the verified GitHub source link. Publication completed on 2026-10-20 at HF commit
`73ec2e61a28e7075c746c8ea573342a7613429af`. Public downloads of the card and
JSONL match the local export byte for byte. All six rows have `synthetic: true`.
The Dataset Viewer renders the `example` split with six rows. No model was called.

HF documentation: https://huggingface.co/docs/hub/datasets-cards and
https://huggingface.co/docs/hub/datasets-adding.

## Release sequence

1. Publish the research starter with synthetic examples and invite methodological
   review. Label it exploratory throughout.
2. Audit real source feasibility and rights, and finalize sampling and judgments.
3. Publish an immutable registered protocol before the first real model run.
4. Run the bounded pilot, record model versions/costs/errors and obtain expert
   review. Publish limitations, failures and negative findings.
5. Release permitted data and the report with exact reproduction instructions.

## Distinct publishing surfaces

- Website: permanent method, source ledger, amendments and an understandable
  explanation of the study. Position the work alongside The House Somm and
  the Service Audit without claiming unmeasured product benefits.
- Substack: “What would it take to show your working in wine criticism?” Tell
  the reporting story and explain why the answer is still open. Lead tags with
  Wine and Hospitality; convert links to absolute website URLs.
- LinkedIn: one operator's argument about auditability. No link or hashtags in
  the body; put the method link in the first comment.
- Reddit: contribute a native, link-free question about evidence requirements
  for estate-wide assessments; do not repost the launch essay.
- GitHub: a concrete reproducible method and contribution requests.
- HF: clear dataset card, permitted rows, grouping, limitations and provenance.

No launch copy should say AI beats Michelin, is unbiased, or can taste wine.
Contact Michelin and any producers discussed in contested reporting through
human-approved outreach before publication; the starter sends no messages.
