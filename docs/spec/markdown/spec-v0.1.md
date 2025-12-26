# TRIX Engine Kernel v0.1 (geometry-first)

> Legacy draft. Current specs live in `src/geometry_core/spec/TRIX_KERNEL_v0_3.md` and
> `src/geometry_core/spec/MATRIX_JUNCTION_v0_2.md`. CLI paths below match the repo layout.

This kernel is **not** "a bunch of markdown links".
It treats your ASCII matrix geometry as the **primary structure** and everything else (docs, tasks, code, steering) as **facets attached to cells**.

Your docs define:
- Titles are encased in square brackets `[]`.
- Base **block** is 3x3 (9 cells).
- Higher order: **9ode** (3x3 of blocks), **super** (3x3 of 9odes), and **cluster** (9x9 view/representation).
- Blocks must be able to **plug in / merge / transform** other blocks.

This engine does three things:
1) Parse **your ASCII matrix skins** into a canonical AST (cells + coordinates).
2) Resolve each cell to a **multi-faceted record** (task/doc/code/config/steer/etc.) via mapping.
3) Provide a zoomable API (CLI for now) to navigate block -> 9ode -> super, and to build "agent context bundles".

## File types

### `.trix` : geometry (ASCII)
A `.trix` file contains the ASCII matrix (any skin), e.g. Parthanon:

```
==[TASK]=======
- [1] [2] [3] -
- [4] [5] [6] -
- [7] [8] [9] -
===============
```

The parser extracts:
- `titl`: `TASK`
- `cells`: 3 rows x 3 cols of raw cell tokens

### `.map.yaml` : meaning (multi-facet binding)
A mapping binds each cell token to either:
- a node record (multi-facet payload), or
- a child matrix (plug-in / zoom target)

Example (cell "5" is a node with multiple facets):
```yaml
cells:
  "5":
    kind: node
    node_id: TASK-5
    facets:
      task: examples/nodes/TASK-5.task.md
      steer: examples/nodes/TASK-5.steer.md
```

Example (cell "1" in hub plugs in another block):
```yaml
cells:
  "1":
    kind: block
    ref: DOCS
    path: examples/blocks/DOCS.trix
```

## CLI
- `python src/trix_py/tools/trix.py parse examples/blocks/TASK.trix`
- `python src/trix_py/tools/trix.py validate examples/blocks/TASK.trix`
- `python src/trix_py/tools/trix.py zoom examples/blocks/HUB0.trix --cell 1`
- `python src/trix_py/tools/trix.py context examples/blocks/TASK.trix --cell 5 --repo .`
- `python src/trix_py/tools/trix.py index examples --out examples/.index.json`

## Where to extend next
- True 9ode/super parsing (3x3 of child matrices).
- Cluster (9x9) derived views.
- Merge/plug operators (mount block into a cell).
- Transforms as first-class nodes (task->code, code->docs).
- Facets as first-class nodes (task->steer, task->config).
- Unified CLI for querying indexed nodes.
