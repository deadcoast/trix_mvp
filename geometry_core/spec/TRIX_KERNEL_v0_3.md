# TRIX Kernel Spec (Geometry-First) — v0.3

This spec is designed to preserve the *geometry as truth*:

- A matrix is a **spatial structure** (cells with coordinates), not a list of links.
- "Skins" are **rendering styles** for the same underlying 3×3 / 1×3 / 9×9 structures.
- Nodes are **multi-facet containers** (task/doc/code/config/steer/log/etc), not just files.

## 1. Core Terms

### Value Types (what a cell can be)
- `node` (`nd`): atomic multi-facet cell
- `9ode` (`9o`): 3×3 grouping of `block`s
- `super` (`su`): 3×3 grouping of `9ode`s

### Modifier Types (what a matrix frame can be)
- `line` (`ln`): 1×3 grouping of its parent value
- `block` (`bk`): 3×3 grouping of its parent value
- `cluster` (`cl`): 9×9 grouping of its parent value

### Design Terms
- `hub`: central `9ode` that serves as organizational root
- `titl`: strict 4-character title token inside `[]` (e.g., `[TASK]`)

## 2. Spatial Coordinates

### Slot numbering for 3×3
Slots are numbered:

1 2 3
4 5 6
7 8 9

Mapping:
- row = (slot-1)//3 + 1
- col = (slot-1)%3 + 1

### Hierarchical addressing
A TRIX address identifies a cell at any depth.

Recommended notation (string):
`<TITL>#<slot>(/<TITL>#<slot>)*`

Examples:
- `TASK#5` (slot 5 inside TASK block)
- `HUB0#2/TASK#5` (TASK lives in slot 2 of HUB0, then select TASK slot 5)

If you want explicit levels:
`HUB0:9o#2/TASK:bk#5`

## 3. Multi-Facet Cells

Every `node` can have 0..N facets. Each facet is typed and points to a payload.

Example binding record:

```yaml
node_id: TASK#5
facets:
  task: nodes/TASK-5.task.md
  steer: nodes/TASK-5.steer.md
  doc: nodes/TASK-5.md
meta:
  status: active
  tags: [dispatch, sprint]
  deps: [ARCH#2]
```

## 4. Composition Operations (the "plug/merge/transform" kernel)

### mount
Mount a matrix (block/9ode/super) into a cell of another matrix.

`mount(target_addr, mounted_matrix_ref)`

### overlay
Merge two matrices of the same shape by coordinate.
Facet merge rules:
- same facet type → choose newest, or keep both with versions
- different facets → union

### splice
Replace a row/col/region in a matrix with another region (same dimensions).

### transform
A transform reads facets/structures and writes facets/structures.

Transforms become first-class cells:
- a node can be `type: transform`
- it declares input addresses and output addresses

## 5. Index / Steering Database

The "database" is an index generated from:
- matrix structures (geometry)
- bindings (node facets + metadata)
- transforms (pipelines)
- junction maps (layout & coordinates)

This index is what agents query to steer work deterministically.

## 6. Skins

Skins are render styles for the same shapes. A parser should:
- recognize known skins (prth/clunk/fcy/boring)
- extract: TITL, 3×3 numeric cells, and their visual coordinates
- ignore decoration
