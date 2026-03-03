# TRIX Engine v0.1 (geometry-first)

- Geometry is parsed from ASCII skins (prth/clunk/etc.)
- Meaning is attached via mapping (multi-facet nodes)
- Index preserves (row/col/slot) so the matrix stays a spatial system

## Quickstart

```sh
python src/trix_py/tools/trix.py validate examples/blocks/TASK.trix
python src/trix_py/tools/trix.py parse examples/blocks/DOCS.trix
python src/trix_py/tools/trix.py zoom examples/blocks/HUB0.trix --cell 1
python src/trix_py/tools/trix.py context examples/blocks/TASK.trix --cell 5 --repo .
python src/trix_py/tools/trix.py index examples --out examples/.index.json
python src/trix_py/tools/trix.py bundle TASK-5 --trix-root src/trix_md --format markdown
python src/trix_py/tools/trix.py dispatch --trix-root src/trix_md --blocks TASK,DOCS --json
```

## Junction validation

```bash
make validate-junction
# optional JSON spec
python src/geometry_core/tools/trix.py validate src/geometry_core/matrix_junction.md --spec src/geometry_core/spec/matrix_junction_ops.json
```

## Junction tooling

```bash
python src/geometry_core/tools/trix.py gutter src/geometry_core/examples/junctions/matrix_junction_example.md
python src/geometry_core/tools/trix.py scan src/geometry_core/examples/junctions/matrix_junction_example.md
python src/geometry_core/tools/trix.py resolve src/geometry_core/examples/junctions/matrix_junction_example.md --lc L0002:C0023
python src/geometry_core/tools/trix.py pin src/geometry_core/examples/junctions/matrix_junction_example.md --repo . --lc L0002:C0023
python src/geometry_core/tools/trix.py content src/geometry_core/examples/junctions/matrix_junction_example.md --repo . --lc L0002:C0023
```

Installed entrypoint (after `uv sync`):

```bash
trix-geometry scan src/geometry_core/examples/junctions/matrix_junction_example.md
```

## Current specs

- Kernel: `src/geometry_core/spec/TRIX_KERNEL_v0_3.md`
- Junctions: `src/geometry_core/spec/MATRIX_JUNCTION_v0_2.md`
- Junction operator grammar: `src/geometry_core/matrix_junction.md`

## Where to extend next
- True 9ode/super parsing (3x3 of child matrices).
- Cluster (9x9) derived views.
- Merge/plug operators (mount block into a cell).
- Transforms as first-class nodes (task->code, code->docs).
- Facets as first-class nodes (task->steer, task->config).
- Query/filter CLI over indexed nodes (status/tags/blocks).
