# TRIX Compounding Specification v0.1

> **Status:** Draft  
> **Depends:** Cell Schema v0.1  
> **Enables:** Composition Operators, Agent Protocol

---

## 1. Purpose

This specification defines the **fractal zoom hierarchy** of TRIX — how nodes compound into blocks, blocks into 9odes, and 9odes into supers. It establishes navigation semantics, addressing conventions, and rendering rules for each level.

The goal is to make TRIX a **zoomable workspace** where you can view projects at any scale from individual tasks to enterprise portfolios.

---

## 2. The Compounding Hierarchy

```
Level     │ Shape          │ Contains           │ Total Nodes
──────────┼────────────────┼────────────────────┼─────────────
node      │ 1×1            │ data               │ 1
block     │ 3×3            │ 9 nodes            │ 9
9ode      │ 3×3 of blocks  │ 9 blocks           │ 81
super     │ 3×3 of 9odes   │ 9 9odes (81 blocks)│ 729
cluster   │ 9×9 view       │ (derived view)     │ 81 (visible)
```

### 2.1 Visual Representation

```
NODE                BLOCK               9ODE                SUPER
┌───┐              ┌───┬───┬───┐       ┌───┬───┬───┐       ┌───┬───┬───┐
│ • │              │ 1 │ 2 │ 3 │       │ B │ B │ B │       │ 9 │ 9 │ 9 │
└───┘              ├───┼───┼───┤       ├───┼───┼───┤       ├───┼───┼───┤
                   │ 4 │ 5 │ 6 │       │ B │ B │ B │       │ 9 │ 9 │ 9 │
                   ├───┼───┼───┤       ├───┼───┼───┤       ├───┼───┼───┤
                   │ 7 │ 8 │ 9 │       │ B │ B │ B │       │ 9 │ 9 │ 9 │
                   └───┴───┴───┘       └───┴───┴───┘       └───┴───┴───┘

                   Each slot holds     Each slot holds     Each slot holds
                   a node              a block (9 nodes)   a 9ode (9 blocks)
```

---

## 3. Level Definitions

### 3.1 Node

The atomic unit of data. A node occupies one cell in a block.

```yaml
level: node
shape: "1×1"
contains: data
has_title: false
has_slots: false
identifer: "{BLOCK}-{slot}"  # e.g., "TASK-5"
```

**A node IS a cell.** The Cell Schema (v0.1) defines its structure.

---

### 3.2 Block

A 3×3 matrix of 9 nodes. The fundamental organizational unit.

```yaml
level: block
shape: "3×3"
contains: 9 nodes
has_title: true             # 4-char titl
has_slots: true             # slots 1-9
identifier: "{TITL}"        # e.g., "TASK"
cell_ids: "{TITL}-{1..9}"   # e.g., "TASK-1" through "TASK-9"
```

**File representation:**
```
blocks/
├── TASK.trix          # ASCII geometry
├── TASK.map.yaml      # cell bindings
└── nodes/
    ├── TASK-1.*.md    # node facets
    └── ...
```

**ASCII example (prth skin):**
```
==[TASK]=======
- [1] [2] [3] -
- [4] [5] [6] -
- [7] [8] [9] -
===============
```

---

### 3.3 9ode (Nine-ode)

A 3×3 matrix of 9 blocks. A higher-order organizational unit.

```yaml
level: 9ode
shape: "3×3 of blocks"
contains: 9 blocks (81 nodes total)
has_title: true             # 4-char titl
has_slots: true             # slots 1-9, each → block_ref
identifier: "{TITL}"        # e.g., "HUB0"
```

**Key distinction:** In a 9ode, each slot contains a **block reference**, not a node.

**File representation:**
```
9odes/
├── HUB0.trix          # ASCII showing 9 block titles
└── HUB0.map.yaml      # slot → block mappings
```

**ASCII example:**
```
==[HUB0]=======
- [DOCS][TASK][CODE] -
- [ARCH][OPER][TEST] -
- [DEPL][LOGS][META] -
===================
```

**Map file:**
```yaml
# HUB0.map.yaml
titl: "HUB0"
kind: "9ode"

cells:
  "1":
    kind: block_ref
    ref: "DOCS"
    path: "blocks/DOCS.trix"
  "2":
    kind: block_ref
    ref: "TASK"
    path: "blocks/TASK.trix"
  # ... etc
```

---

### 3.4 Super

A 3×3 matrix of 9 9odes. The highest organizational tier.

```yaml
level: super
shape: "3×3 of 9odes"
contains: 9 9odes (81 blocks, 729 nodes total)
has_title: true             # 4-char titl
has_slots: true             # slots 1-9, each → 9ode_ref
identifier: "{TITL}"        # e.g., "MAIN"
```

**Use case:** Portfolio/program level management.

**ASCII example:**
```
==[MAIN]=======
- [PROD][ENGR][DATA] -
- [INFR][SECR][PLAT] -
- [SUPP][SALE][EXEC] -
===================
```

Each slot is a 9ode containing 9 blocks each.

---

### 3.5 Cluster (Derived View)

A cluster is NOT a container level — it's a **zoom view** that shows 9×9 cells.

```yaml
level: cluster
shape: "9×9 (view)"
view_of: 9ode | block
purpose: dashboard / overview
is_container: false
```

**Cluster of a 9ode** shows all 81 nodes (9 blocks × 9 nodes):
```
... ... ...    ... ... ...    ... ... ...
... ... ...    ... ... ...    ... ... ...
... ... ...    ... ... ...    ... ... ...

... ... ...    ... ... ...    ... ... ...
... ... ...    ... ... ...    ... ... ...
... ... ...    ... ... ...    ... ... ...

... ... ...    ... ... ...    ... ... ...
... ... ...    ... ... ...    ... ... ...
... ... ...    ... ... ...    ... ... ...
```

---

## 4. Title Conventions

### 4.1 The 4-Character Rule

All titled entities (blocks, 9odes, supers) use exactly 4 characters:

```
[A-Z0-9]{4}
```

**Valid:** `TASK`, `DOCS`, `HUB0`, `CODE`, `TST1`  
**Invalid:** `TASKS` (5 chars), `Doc` (3 chars), `task` (lowercase)

### 4.2 Reserved Titles

| Title | Level | Purpose |
|-------|-------|---------|
| `HUB0` | 9ode | Primary project hub |
| `MAIN` | super | Enterprise root |
| `META` | block | System metadata |
| `LOGS` | block | Event/audit logs |

### 4.3 Naming Patterns (Suggested)

| Pattern | Meaning | Examples |
|---------|---------|----------|
| `XXXX` | Domain name | `DOCS`, `TASK`, `CODE` |
| `XXX0`-`XXX9` | Indexed series | `TST1`, `TST2`, `TST3` |
| `_XXX` | Private/internal | `_TMP`, `_WIP` |

---

## 5. Addressing

### 5.1 Address Format

TRIX uses a path-style addressing scheme:

```
{SUPER}#{9ODE}#{BLOCK}#{slot}
```

**Examples:**
- `TASK#5` — slot 5 of block TASK (relative)
- `HUB0#TASK#5` — slot 5 of TASK within 9ode HUB0
- `MAIN#PROD#HUB0#TASK#5` — full absolute path

### 5.2 Address Components

| Component | Optional | Description |
|-----------|----------|-------------|
| Super | Yes | Top-level super name |
| 9ode | Yes | 9ode name |
| Block | No | Block name (required) |
| Slot | No | Slot number 1-9 (required) |

### 5.3 Resolution Rules

1. **Relative addresses** are resolved from context:
   - In a block context: `5` → `{current_block}#5`
   - In a 9ode context: `TASK#5` → `{current_9ode}#TASK#5`

2. **Absolute addresses** start from a known root:
   - `HUB0#TASK#5` is absolute within a 9ode scope
   - `MAIN#PROD#HUB0#TASK#5` is fully absolute

3. **Lookup** traverses the hierarchy:
   ```
   MAIN#PROD#HUB0#TASK#5
     │    │    │    │  └─ slot 5 of TASK block
     │    │    │    └──── TASK block (slot ? of HUB0)
     │    │    └───────── HUB0 9ode (slot ? of PROD)
     │    └────────────── PROD 9ode (slot ? of MAIN)
     └─────────────────── MAIN super (root)
   ```

---

## 6. Navigation

### 6.1 Zoom Operations

**Zoom In:** Enter a referenced matrix
```
Current: HUB0 (9ode view)
Action:  zoom_in(slot=2)  # slot 2 = TASK block_ref
Result:  TASK (block view)
```

**Zoom Out:** Return to parent container
```
Current: TASK (block view)
Action:  zoom_out()
Result:  HUB0 (9ode view, with TASK highlighted at slot 2)
```

### 6.2 Navigation State

```yaml
navigation:
  current_level: block | 9ode | super
  current_titl: string
  parent_path: list[string]   # breadcrumb
  child_refs: map[slot, titl] # available zoom targets
```

**Example state:**
```yaml
navigation:
  current_level: block
  current_titl: "TASK"
  parent_path: ["MAIN", "PROD", "HUB0"]
  child_refs: {}  # blocks don't contain matrix refs (nodes only)
```

### 6.3 Breadcrumb Display

```
MAIN > PROD > HUB0 > TASK > [5]
└─super─┘ └─9ode─┘ └block┘ └slot
```

---

## 7. Slot Mapping Across Levels

Each level uses slots 1-9, but the meaning differs:

| Level | Slot Contains | Cell Kind |
|-------|---------------|-----------|
| Block | Node | `node` |
| 9ode | Block reference | `block_ref` |
| Super | 9ode reference | `9ode_ref` |

### 7.1 Cross-Level Addressing

To address a specific node from a super:

```
MAIN#3#2#5
  │  │ │ └─ slot 5 of the block
  │  │ └─── slot 2 of the 9ode (the block)
  │  └───── slot 3 of the super (the 9ode)
  └──────── super name
```

This numeric form is useful for computed access.

### 7.2 Named vs Numeric

Both are valid:
- Named: `MAIN#PROD#HUB0#TASK#5`
- Numeric: `MAIN#3#2#5`

Named is human-readable; numeric is machine-efficient.

---

## 8. Rendering

### 8.1 Block Rendering

Blocks render their 9 node tokens:

```
==[TASK]=======
- [1] [2] [3] -
- [4] [5] [6] -
- [7] [8] [9] -
===============
```

### 8.2 9ode Rendering

9odes render their 9 block titles:

**Compact (one line per block):**
```
==[HUB0]=======
[DOCS][TASK][CODE]
[ARCH][OPER][TEST]
[DEPL][LOGS][META]
===============
```

**Verbose (inline blocks):**
```
==[DOCS]===  ==[TASK]===  ==[CODE]===
[1][2][3]    [1][2][3]    [1][2][3]
[4][5][6]    [4][5][6]    [4][5][6]
[7][8][9]    [7][8][9]    [7][8][9]
===========  ===========  ===========
```

### 8.3 Cluster Rendering (9×9 view)

Derived from a 9ode, showing all 81 cells:

```
... ... ...  ... ... ...  ... ... ...
... ... ...  ... ... ...  ... ... ...
... ... ...  ... ... ...  ... ... ...

... ... ...  ... ... ...  ... ... ...
... ... ...  ... ... ...  ... ... ...
... ... ...  ... ... ...  ... ... ...

... ... ...  ... ... ...  ... ... ...
... ... ...  ... ... ...  ... ... ...
... ... ...  ... ... ...  ... ... ...
```

### 8.4 Skin Independence

All levels support multiple ASCII skins:
- `prth` (Parthanon)
- `clunk`
- `fcy` (Fancy)
- `boring`

The parser extracts geometry regardless of skin.

---

## 9. Compound Metrics

### 9.1 Scale Table

| Structure | Nodes | Blocks | 9odes | Dimension |
|-----------|-------|--------|-------|-----------|
| Node | 1 | — | — | 1×1 |
| Block | 9 | 1 | — | 3×3 |
| 9ode | 81 | 9 | 1 | 9×9 |
| Super | 729 | 81 | 9 | 27×27 |
| Super² | 6,561 | 729 | 81 | 81×81 |

### 9.2 Compounding Formula

```
nodes_at_level(n) = 9^n

Level 0 (node):  9^0 = 1
Level 1 (block): 9^1 = 9
Level 2 (9ode):  9^2 = 81
Level 3 (super): 9^3 = 729
```

---

## 10. Rollup Semantics

Higher levels can display **aggregated status** from children:

### 10.1 Status Rollup

A 9ode slot's status derives from its referenced block:

```yaml
rollup_rules:
  - if all_children(done): parent = done
  - if any_children(blocked): parent = blocked
  - if any_children(active): parent = active
  - else: parent = draft
```

### 10.2 Completion Percentage

```
9ode_completion = sum(block_completion for block in children) / 9
block_completion = count(status=done) / 9
```

### 10.3 Priority Propagation

The highest priority (lowest number) among children bubbles up:

```yaml
9ode_priority = min(block.priority for block in children if block.priority)
```

---

## 11. File Organization

### 11.1 Recommended Structure

```
project/
├── super/
│   └── MAIN.trix
├── 9odes/
│   ├── PROD.trix
│   ├── ENGR.trix
│   └── ...
├── blocks/
│   ├── TASK/
│   │   ├── TASK.trix
│   │   ├── TASK.map.yaml
│   │   └── nodes/
│   ├── DOCS/
│   └── ...
└── .trix/
    └── index.json
```

### 11.2 Flat Structure (Alternative)

```
project/
├── matrices/
│   ├── MAIN.super.trix
│   ├── PROD.9ode.trix
│   ├── TASK.block.trix
│   └── ...
└── nodes/
    ├── TASK-1.task.md
    └── ...
```

---

## 12. Validation Rules

### 12.1 Structural Rules

- A block must have exactly 9 cells (slots 1-9)
- A 9ode must have exactly 9 block_refs (slots 1-9)
- A super must have exactly 9 9ode_refs (slots 1-9)

### 12.2 Reference Integrity

- All `ref` values must point to existing matrices
- No circular references (A→B→C→A)
- A block cannot contain block_refs (only nodes)

### 12.3 Title Uniqueness

- Block titles must be unique within a 9ode
- 9ode titles must be unique within a super
- Global uniqueness is recommended but not required

---

## 13. Future Extensions

### 13.1 Dynamic Compounding

Allow blocks to be "promoted" to 9odes by splitting cells into sub-blocks.

### 13.2 Virtual 9odes

9odes defined by query rather than explicit structure:
```yaml
kind: virtual_9ode
query: "status=active AND tag=mvp"
```

### 13.3 Cross-Super References

Allow supers to reference blocks in other supers for shared resources.

---

## Appendix A: Compounding Math

The doubling sequence from your design lib:

```
3×3 → 6×6 → 12×12 → 24×24 → 48×48 → ...
```

This represents **cell dimensions**, not container levels. The relationship:

| Level | Container Dim | Cell Dim (if expanded) |
|-------|---------------|------------------------|
| Block | 1×1 | 3×3 cells |
| 9ode | 3×3 blocks | 9×9 cells |
| Super | 3×3 9odes | 27×27 cells |

---

## Appendix B: Changelog

| Version | Date | Changes |
|---------|------|---------|
| v0.1 | 2024-XX-XX | Initial specification |
