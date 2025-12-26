# trix_geometry_core

Geometry-first helpers for TRIX:
- gutter overlay (L/C) for pinpoint references
- parse/scan embedded 3×3 blocks in ASCII skins
- build a repo index of embedded blocks

## Quickstart

```bash
python tools/trix.py gutter examples/junctions/matrix_junction_example.md
python tools/trix.py parse examples/blocks/TASK.trix
python tools/trix.py scan examples/junctions/matrix_junction_example.md
python tools/trix.py index . --out .trix/index.json
python tools/trix.py validate ../geometry_core/matrix_junction.md --spec ../geometry_core/spec/matrix_junction_ops.yaml
python tools/trix.py validate ../geometry_core/matrix_junction.md --spec ../geometry_core/spec/matrix_junction_ops.json
```

From repo root:

```bash
make validate-junction
```

This scaffold is meant to be merged into your TRIX repo and extended to match your
full `matrix_junction.md` semantics (mount/merge/transform, multi-level compounding, etc).
