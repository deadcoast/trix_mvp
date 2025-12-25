# Repository Guidelines

## Project Structure & Module Organization
The repository is documentation-only. Active content lives in `notes/`, organized by topic:
- `notes/formats/` holds format definitions (for example `notes/formats/DevDecimal++/`).
- `notes/version_control/` contains versioning examples and comparisons.
- `notes/templates/` provides starter templates.
- `notes/metadata/` stores supporting references.

The `framework_drafts/` and `hierarchical_taxonomy/` directories are currently empty placeholders; add new material there only if you are expanding those areas intentionally.

## Build, Test, and Development Commands
There are no build or test scripts in this repository. If you use Markdown linting locally, point it at the repo-level config:
- `markdownlint "**/*.md"` (uses `.markdownlint.json`).

## Coding Style & Naming Conventions
This repo follows the DevDecimal++ document format:
- File paths: `NN_Top-Level/NN.MM_Page-Slug.md` (zero-padded IDs).
- Headings: `# [NN.MM] Title`, major sections `## [NN.MM.10] ...` (slot by tens).
- Slugs allow `A-Z a-z 0-9 _ - .` and no spaces.

Keep IDs stable; insert new sections by slotting (for example `.15`, `.25`) instead of renumbering. Use the required header block and section order defined in `notes/formats/DevDecimal++/DocPageContract.md`.

Markdown style is enforced by `.markdownlint.json`: dash lists, 2-space list indentation, and fenced code blocks with backticks.

## Testing Guidelines
There are no automated tests. Validate changes by checking:
- Heading IDs match the filename prefix.
- Section order follows the Doc Page Contract.
- `status`, `review_cycle`, and `last_verified` are set in the header block.

## Commit & Pull Request Guidelines
This checkout does not include Git history, so there are no repo-specific commit conventions to cite. If you open a PR:
- Summarize what changed and why, and list the affected doc IDs (for example `02.20.40.03`).
- Call out any renumbering or structural moves explicitly.
- Include before/after examples for major structure changes.

## Templates & References
Prefer existing templates in `notes/templates/` or the “New Page Template” in `notes/formats/DevDecimal++/DocPageContract.md` to keep formatting consistent.
