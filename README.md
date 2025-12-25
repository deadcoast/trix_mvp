# TRIX Engine v0.1 (geometry-first)

This scaffold proves one thing: **we can keep your ASCII matrix design as the canonical truth** and still have a queryable steering database.

- Geometry is parsed from ASCII skins (prth/clunk/etc.)
- Meaning is attached via mapping (multi-facet nodes)
- Index preserves (row/col/slot) so the matrix stays a spatial system

## Quickstart

```bash
python tools/trix.py validate examples/blocks/TASK.trix
python tools/trix.py parse examples/blocks/DOCS.trix
python tools/trix.py zoom examples/blocks/HUB0.trix --cell 1
python tools/trix.py context examples/blocks/TASK.trix --cell 5 --repo .
python tools/trix.py index examples --out examples/.index.json
```

## Where to extend next
- True 9ode/super parsing (3x3 of child matrices).
- Cluster (9x9) derived views.
- Merge/plug operators (mount block into a cell).
- Transforms as first-class nodes (task->code, code->docs).
- Facets as first-class nodes (task->steer, task->config).
- CLI for zooming, context, and next task.