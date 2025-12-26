# trix_geometry_core

Geometry-first helpers for TRIX:
- gutter overlay (L/C) for pinpoint references
- parse/scan embedded 3×3 blocks in ASCII skins
- build a repo index of embedded blocks

## Quickstart

```bash
python src/geometry_core/tools/trix.py gutter src/geometry_core/examples/junctions/matrix_junction_example.md
python src/geometry_core/tools/trix.py scan src/geometry_core/examples/junctions/matrix_junction_example.md
python src/geometry_core/tools/trix.py resolve src/geometry_core/examples/junctions/matrix_junction_example.md --lc L0002:C0023
python src/geometry_core/tools/trix.py pin src/geometry_core/examples/junctions/matrix_junction_example.md --repo . --lc L0002:C0023
python src/geometry_core/tools/trix.py content src/geometry_core/examples/junctions/matrix_junction_example.md --repo . --lc L0002:C0023
python src/geometry_core/tools/trix.py index . --out .trix/index.json
python src/geometry_core/tools/trix.py validate src/geometry_core/matrix_junction.md --spec src/geometry_core/spec/matrix_junction_ops.yaml
python src/geometry_core/tools/trix.py validate src/geometry_core/matrix_junction.md --spec src/geometry_core/spec/matrix_junction_ops.json
```

Module entrypoint (from repo root):

```bash
PYTHONPATH=src python -m geometry_core.tools.trix scan src/geometry_core/examples/junctions/matrix_junction_example.md
```

Installed entrypoint (after `uv sync`):

```bash
trix-geometry scan src/geometry_core/examples/junctions/matrix_junction_example.md
```

From repo root:

```bash
make validate-junction
```

This scaffold is meant to be merged into your TRIX repo and extended to match your
full `matrix_junction.md` semantics (mount/merge/transform, multi-level compounding, etc).
