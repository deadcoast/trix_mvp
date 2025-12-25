# Repository Guidelines

## Project Structure & Module Organization
- `src/trix_py/` contains the geometry-first parser/indexer library and the main CLI in `tools/trix.py`.
- `src/geometry_core/` provides lower-level geometry helpers, junction tooling, and core specs.
- `src/trix_md/` holds Markdown matrix scaffolds (`blocks/`, `hub/`) and a lightweight MVP CLI.
- `examples/` stores sample `.trix`, `.map.yaml`, and node facet files for validation and indexing.
- `docs/` captures specs and notes, with primary references in `docs/spec/markdown/`.

## Build, Test, and Development Commands
- `python src/trix_py/tools/trix.py validate examples/blocks/TASK.trix` validates a 3x3 block.
- `python src/trix_py/tools/trix.py parse examples/blocks/DOCS.trix` parses a `.trix` file to JSON.
- `python src/trix_py/tools/trix.py index examples --out examples/.index.json` builds an example index.
- `python src/geometry_core/tools/trix.py scan src/geometry_core/examples/junctions/matrix_junction_example.md` scans for embedded matrices.
- `python -m pytest` runs tests (looks under `tests/`, which may be empty).
- Python >= 3.13 is required per `pyproject.toml`.

## Coding Style & Naming Conventions
- Python: 4-space indentation, Black formatting (`line-length = 120`, skip string normalization), isort with the Black profile, and strict mypy.
- Domain naming: block titles are 4-char tokens like `[DOCS]`, with slots `[1]..[9]`.
- Example conventions: keep `.trix` blocks in `examples/blocks/` and node facets named like `TASK-5.task.md`.

## Testing Guidelines
- Use pytest and pytest-cov (configured in `pyproject.toml`).
- New tests should live in `tests/` and follow `test_*.py` naming.
- When changing parsing or indexing behavior, add coverage using representative `.trix` examples.

## Commit & Pull Request Guidelines
- Commit messages follow a conventional style seen in history (for example, `feat: add geometry-first helper tools`).
- PRs should describe behavior changes, list updated example/spec files, and include sample CLI output when parsing or indexing changes.
