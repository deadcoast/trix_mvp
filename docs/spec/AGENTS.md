# Repository Guidelines

## Project Structure & Module Organization
- `src/trix_py/` holds the geometry-first parser/indexer library and CLI at `src/trix_py/tools/trix.py`.
- `src/geometry_core/` owns junction tooling and specs (`src/geometry_core/spec/`, `src/geometry_core/tools/`).
- `src/trix_md/` contains the Markdown matrix workspace (`blocks/`, `hub/`) and a small CLI.
- `examples/` provides sample `.trix` blocks, `.map.yaml` bindings, and facet files.
- `docs/spec/` collects legacy specs; current canonical specs live under `src/geometry_core/spec/`.

## Build, Test, and Development Commands
- `uv sync` installs dependencies (Python 3.13+).
- `python src/trix_py/tools/trix.py validate examples/blocks/TASK.trix` validates a `.trix` block.
- `python src/geometry_core/tools/trix.py validate src/geometry_core/matrix_junction.md --spec src/geometry_core/spec/matrix_junction_ops.yaml` validates junction operators.
- `python src/trix_md/tools/trix.py index --repo src/trix_md` builds the Markdown workspace index.
- `python -m pytest` runs tests (pytest discovers under `src/`).

## Coding Style & Naming Conventions
- Python: Black (line length 120), isort (Black profile), mypy (strict) per `pyproject.toml`.
- Block titles are 4-char tokens like `[TASK]`; slots are `[1]..[9]`.
- Facet files follow `<NODE_ID>.<facet>.md` (for example `TASK-5.task.md`).

## Testing Guidelines
- Add tests in `src/trix_py/lib/test_early_indexer/` or under `tests/` if introduced.
- When changing junction parsing or specs, update `src/geometry_core/matrix_junction.md` and re-run validation.
- For doc-only edits, optionally run `markdownlint "**/*.md"` (uses `.markdownlint.json`).

## Commit & Pull Request Guidelines
- Use conventional commit prefixes (`feat:`, `fix:`, `docs:`).
- PRs should summarize spec/CLI changes, list affected docs, and include sample CLI output when behavior changes.
