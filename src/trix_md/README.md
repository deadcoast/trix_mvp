# trix MVP scaffold

This repo is a starter structure for a **trix** (Modular Matrix Workflow) ecosystem:
- Markdown matrices as the human UI
- YAML front-matter as machine-readable metadata
- A tiny CLI to validate + index matrices and pick next tasks

> This is intentionally minimal and opinionated so you have something you can run today.

## Quick start

```bash
python tools/trix.py validate
python tools/trix.py index
python tools/trix.py next
```

## Layout

- `trix/hub/` — your central *hub* 9ode (3x3 of blocks)
- `trix/blocks/<TITL>/matrix.md` — a block (3x3 of nodes)
- `trix/blocks/<TITL>/nodes/<1-9>.md` — the 9 node files inside a block
- `trix/.index/trix_index.json` — generated index

## Conventions (MVP)

- Block titles are 4 chars: `[DOCS]`, `[TASK]`, etc.
- Node slots are `[1]`..`[9]` and link to files.
- Every matrix is 3 rows x 3 columns.

You can extend/replace any of this later.
