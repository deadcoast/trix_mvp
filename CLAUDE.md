# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TRIX is a geometry-first ASCII matrix parsing engine. It treats ASCII art 3×3 matrices as the canonical truth while maintaining a queryable steering database. The core idea: geometry is parsed from ASCII "skins," meaning is attached via YAML mappings, and spatial (row/col/slot) coordinates are preserved throughout.

## Build & Development Commands

```bash
# Install dependencies (requires Python 3.13+)
uv sync

# Run tests
python -m pytest

# Lint/format
black src/
isort src/
mypy src/trix tests/
```

## CLI Tools

There are three separate CLI tools in different modules:

**Primary Parser (trix_py)**:
```bash
python src/trix_py/tools/trix.py validate examples/blocks/TASK.trix
python src/trix_py/tools/trix.py parse examples/blocks/DOCS.trix
python src/trix_py/tools/trix.py index examples --out examples/.index.json
python src/trix_py/tools/trix.py zoom examples/blocks/HUB0.trix --cell 5
python src/trix_py/tools/trix.py context examples/blocks/TASK.trix --cell 5 --repo .
python src/trix_py/tools/trix.py bundle TASK-5 --trix-root src/trix_md --format markdown
python src/trix_py/tools/trix.py dispatch --trix-root src/trix_md --blocks TASK --json
```

**Geometry Core (junction scanning, multi-matrix)**:
```bash
python src/geometry_core/tools/trix.py gutter <file>           # Add L/C gutters
python src/geometry_core/tools/trix.py scan <file>             # Find all embedded 3×3 blocks
python src/geometry_core/tools/trix.py resolve <file> --lc L42:C100  # Resolve coordinate to matrix+slot
python src/geometry_core/tools/trix.py addr --slot 5           # Convert slot↔row/col
python src/geometry_core/tools/trix.py pin <file> --repo . --lc L42:C100    # Resolve to binding + facet excerpts
python src/geometry_core/tools/trix.py content <file> --repo . --lc L42:C100 # Resolve to full facet contents
python src/geometry_core/tools/trix.py validate <file> --spec src/geometry_core/spec/matrix_junction_ops.yaml
```

**Markdown MVP (trix_md)**:
```bash
python src/trix_md/tools/trix.py validate --repo src/trix_md
python src/trix_md/tools/trix.py index --repo src/trix_md
python src/trix_md/tools/trix.py next --repo src/trix_md
```

## Architecture

### Module Structure

- **`src/trix_py/`**: Core parser/indexer library
  - `lib/parser.py`: Extracts `TrixMatrix` AST from `.trix` files (skin-agnostic)
  - `lib/indexer.py`: Builds `MatrixRecord` with cell bindings from YAML mappings
  - `tools/trix.py`: CLI for parse/validate/index/zoom/context/bundle/dispatch

- **`src/geometry_core/`**: Low-level geometry helpers
  - `tools/trix.py`: Junction scanning, gutter overlays, coordinate resolution, validation, pin/content
  - `tools/junction_validate.py`: Data-driven operator validation helpers
  - Handles side-by-side matrices in a single file

- **`src/trix_md/`**: Markdown-based matrix scaffold
  - `blocks/<TITL>/matrix.md` + `nodes/{1-9}.md` structure and `hub/*.md` entrypoints
  - YAML front matter for metadata
  - `.index/trix_index.json` for the generated index

### Key Domain Concepts

- **Block**: A 3×3 matrix with slots `[1]..[9]`, titled with 4-char tokens like `[DOCS]`, `[TASK]`
- **Slot**: Position 1-9 in reading order (left-to-right, top-to-bottom)
- **Skin**: Visual ASCII style (prth, clunk, fcy, boring) — parser is skin-agnostic
- **Node**: Content bound to a slot, can have multiple facets (`.task.md`, `.steer.md`)
- **Junction Canvas**: A file containing multiple side-by-side matrices with gutter coordinates
- **9ode/Super**: Higher-level 3×3 of blocks (not fully implemented)

### Coordinate Systems

Slot-to-coordinate mapping for 3×3:
```
[1][2][3]  →  slot 1-3 = row 1
[4][5][6]  →  slot 4-6 = row 2
[7][8][9]  →  slot 7-9 = row 3
```

Junction files use `vlg`/`hlg` (vertical/horizontal line gutters) or `L####:C####` overlay coordinates.

### File Conventions

- `.trix`: ASCII matrix files (various skins)
- `.map.yaml`: Cell-to-meaning mappings (`examples/maps/TASK.map.yaml`)
- Node facets: `<NODE_ID>.<facet>.md` (e.g., `TASK-5.task.md`, `TASK-5.steer.md`)

## Code Style

- Black formatting with `line-length = 120`, skip string normalization
- isort with Black profile
- Strict mypy (all `disallow_*` flags enabled)
- Commit messages: `feat:`, `fix:`, `docs:` prefixes
