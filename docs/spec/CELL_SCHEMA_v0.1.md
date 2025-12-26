# TRIX Cell Schema Specification v0.1

> **Status:** Draft  
> **Depends:** None (foundation spec)  
> **Enables:** Composition Operators, Agent Protocol

---

## 1. Purpose

This specification defines the canonical structure of a **TRIX cell** — the atomic unit of the matrix system. A cell is not a simple value; it is a **multi-facet capsule** that can hold task definitions, documentation, steering constraints, code references, and more simultaneously.

The goal is to transform TRIX from "ASCII diagrams with links" into a **queryable steering database** where each cell is a structured record with known fields.

---

## 2. Core Principles

### 2.1 Geometry is Truth
A cell's position (slot, row, col) is **immutable** once assigned. The geometry comes from parsing the ASCII matrix; the schema attaches meaning to that geometry.

### 2.2 Facets are Attachments, Not the Cell
A cell can have zero, one, or many facets. The cell exists even if all facets are empty — it still occupies its slot in the 3×3 grid.

### 2.3 Extensible Facet Types
While we define a core set of facet types, the system allows arbitrary facet names for future expansion.

---

## 3. Cell Identity

Every cell has a unique identity derived from its position:

```yaml
cell_id: "{BLOCK}-{slot}"
```

**Examples:**
- `TASK-5` — slot 5 of the TASK block
- `DOCS-1` — slot 1 of the DOCS block
- `HUB0-3` — slot 3 of the HUB0 9ode

### 3.1 Identity Fields

| Field | Type | Description |
|-------|------|-------------|
| `cell_id` | string | Canonical identifier `{BLOCK}-{slot}` |
| `block` | string | Parent matrix title (4-char) |
| `slot` | int | Position 1..9 in reading order |
| `row` | int | Row 1..3 (derived from slot) |
| `col` | int | Column 1..3 (derived from slot) |

### 3.2 Slot-to-Coordinate Mapping

```
Slot → (Row, Col)
─────────────────
  1  →  (1, 1)    2  →  (1, 2)    3  →  (1, 3)
  4  →  (2, 1)    5  →  (2, 2)    6  →  (2, 3)
  7  →  (3, 1)    8  →  (3, 2)    9  →  (3, 3)
```

**Formulas:**
```
row = ((slot - 1) // 3) + 1
col = ((slot - 1) % 3) + 1
slot = (row - 1) * 3 + col
```

---

## 4. Cell Classification

A cell's `kind` determines how it's interpreted by the system:

| Kind | Description | Contains |
|------|-------------|----------|
| `node` | Atomic data unit | Facets with content |
| `block_ref` | Portal to another block | Reference to a 3×3 matrix |
| `9ode_ref` | Portal to a 9ode | Reference to a 3×3 of blocks |
| `super_ref` | Portal to a super | Reference to a 3×3 of 9odes |
| `empty` | Unoccupied slot | No content (placeholder) |

### 4.1 Reference Cells

When `kind` is `block_ref`, `9ode_ref`, or `super_ref`, the cell acts as a **zoom portal**:

```yaml
kind: block_ref
ref: "DOCS"              # target matrix title
path: "blocks/DOCS.trix" # optional: explicit path
```

---

## 5. Facets

Facets are the multi-attachment system that gives cells their semantic richness. Each facet is a typed slot that can hold a file path (external content) or inline data.

### 5.1 Core Facet Types

| Facet | Purpose | Typical Extension |
|-------|---------|-------------------|
| `task` | Actionable work item | `.task.md` |
| `doc` | Documentation/narrative | `.doc.md` |
| `steer` | Agent constraints/instructions | `.steer.md` |
| `code` | Source code reference | `.py`, `.ts`, etc. |
| `config` | Configuration data | `.yaml`, `.toml`, `.json` |
| `log` | Execution history | `.log.md` |
| `metric` | Measurements/KPIs | `.metric.yaml` |

### 5.2 Facet Structure

Each facet can be:

**Path reference (external file):**
```yaml
facets:
  task: "nodes/TASK-5.task.md"
  steer: "nodes/TASK-5.steer.md"
```

**Inline content (embedded):**
```yaml
facets:
  task:
    inline: true
    content: |
      - [ ] Implement the parser
      - [ ] Write tests
```

**Null (not present):**
```yaml
facets:
  task: null  # or omitted entirely
```

### 5.3 Custom Facets

The facet system is extensible. Any string key is valid:

```yaml
facets:
  task: "..."
  doc: "..."
  review: "nodes/TASK-5.review.md"      # custom
  security: "nodes/TASK-5.security.md"  # custom
```

Tools should recognize core facet types and pass through unknown types.

---

## 6. Steering Metadata

Beyond facets, cells carry metadata used for project steering and dispatch:

### 6.1 Status

```yaml
status: enum
```

| Value | Meaning |
|-------|---------|
| `draft` | Not ready for work |
| `active` | Currently being worked on |
| `blocked` | Waiting on dependencies |
| `done` | Completed |
| `archived` | No longer relevant |

**State transitions:**
```
draft → active → done → archived
          ↓
       blocked → active
```

### 6.2 Priority

```yaml
priority: int | null
```

- `1` = Highest (critical)
- `2` = High
- `3` = Medium (default)
- `4` = Low
- `5` = Lowest (nice-to-have)
- `null` = Unprioritized

### 6.3 Dependencies

```yaml
deps: list[cell_id]
```

Dependencies are other cells that must reach `done` status before this cell can be worked on:

```yaml
deps:
  - "ARCH-2"   # Design must be done first
  - "DOCS-5"   # Spec must be written first
```

**Dispatch rule:** A cell with `status: active` but unmet deps is treated as `blocked`.

### 6.4 Tags

```yaml
tags: list[string]
```

Free-form labels for filtering and grouping:

```yaml
tags:
  - "mvp"
  - "backend"
  - "p1-sprint"
```

### 6.5 Owner

```yaml
owner: string | null
```

The entity responsible for this cell:

```yaml
owner: "@alice"          # human
owner: "agent:codegen"   # AI agent
owner: null              # unassigned
```

---

## 7. Links

Cells can reference other cells with typed relationships:

```yaml
links:
  - target: cell_id
    relation: enum
```

### 7.1 Relation Types

| Relation | Meaning |
|----------|---------|
| `requires` | This cell needs the target to function |
| `produces` | This cell generates the target |
| `extends` | This cell builds upon the target |
| `see_also` | Related reference (non-blocking) |
| `blocks` | This cell prevents target from starting |

**Example:**
```yaml
links:
  - target: "CODE-5"
    relation: "produces"
  - target: "DOCS-3"
    relation: "extends"
  - target: "ARCH-2"
    relation: "requires"
```

---

## 8. Complete Cell Schema

### 8.1 YAML Schema

```yaml
# cell.schema.yaml

cell:
  # === Identity (immutable, from geometry) ===
  cell_id: string          # format: "{BLOCK}-{slot}"
  block: string            # parent matrix title (4-char)
  slot: int                # 1..9
  row: int                 # 1..3 (derived)
  col: int                 # 1..3 (derived)
  
  # === Classification ===
  kind: enum               # node | block_ref | 9ode_ref | super_ref | empty
  
  # === Reference (for *_ref kinds) ===
  ref: string | null       # target matrix title
  path: string | null      # optional explicit path
  
  # === Facets (multi-attachment) ===
  facets:
    task: path | inline | null
    doc: path | inline | null
    steer: path | inline | null
    code: path | inline | null
    config: path | inline | null
    log: path | inline | null
    metric: path | inline | null
    # ... extensible with custom keys
  
  # === Steering Metadata ===
  status: enum             # draft | active | blocked | done | archived
  priority: int | null     # 1..5 or null
  deps: list[cell_id]      # blocking dependencies
  tags: list[string]       # free-form labels
  owner: string | null     # responsible entity
  
  # === Links ===
  links:
    - target: cell_id
      relation: enum       # requires | produces | extends | see_also | blocks
```

### 8.2 Example: Fully Populated Cell

```yaml
cell_id: "TASK-5"
block: "TASK"
slot: 5
row: 2
col: 2

kind: "node"

facets:
  task: "nodes/TASK-5.task.md"
  steer: "nodes/TASK-5.steer.md"
  doc: null
  code: null
  config: null
  log: "nodes/TASK-5.log.md"
  metric: null

status: "active"
priority: 2
deps:
  - "ARCH-2"
  - "DOCS-3"
tags:
  - "mvp"
  - "parser"
owner: "agent:codegen"

links:
  - target: "CODE-5"
    relation: "produces"
  - target: "DOCS-5"
    relation: "produces"
```

### 8.3 Example: Reference Cell (Block Portal)

```yaml
cell_id: "HUB0-1"
block: "HUB0"
slot: 1
row: 1
col: 1

kind: "block_ref"
ref: "DOCS"
path: "blocks/DOCS.trix"

facets: {}        # refs typically don't have their own facets
status: null      # status is on the referenced block, not the portal
priority: null
deps: []
tags: []
owner: null
links: []
```

---

## 9. Slot Semantics (Default Convention)

While slots 1-9 can hold any content, the following default semantics enable consistent interpretation across blocks:

| Slot | Name | Purpose |
|------|------|---------|
| 1 | Charter | Mission/scope definition |
| 2 | Inputs | Required resources/data |
| 3 | References | External docs/links |
| 4 | Backlog | Queued work items |
| 5 | Now | Current active work |
| 6 | Decisions | Choices made, rationale |
| 7 | Outputs | Produced artifacts |
| 8 | Validation | Tests, reviews, QA |
| 9 | Logs | History, metrics, notes |

**Visual:**
```
┌─────────┬─────────┬─────────┐
│ Charter │ Inputs  │  Refs   │
│   [1]   │   [2]   │   [3]   │
├─────────┼─────────┼─────────┤
│ Backlog │   NOW   │Decisions│
│   [4]   │   [5]   │   [6]   │
├─────────┼─────────┼─────────┤
│ Outputs │Validate │  Logs   │
│   [7]   │   [8]   │   [9]   │
└─────────┴─────────┴─────────┘
```

This is a **convention**, not a constraint. Blocks may override with their own semantics.

---

## 10. Storage Conventions

### 10.1 Mapping Files

Cell metadata is stored in `.map.yaml` files alongside `.trix` geometry files:

```
blocks/
├── TASK.trix          # ASCII geometry
├── TASK.map.yaml      # cell bindings + metadata
└── nodes/
    ├── TASK-5.task.md
    └── TASK-5.steer.md
```

### 10.2 Map File Structure

```yaml
# TASK.map.yaml

titl: "TASK"
kind: "block"

cells:
  "1":
    kind: "node"
    status: "done"
    facets:
      doc: "nodes/TASK-1.doc.md"
      
  "5":
    kind: "node"
    status: "active"
    priority: 2
    deps: ["ARCH-2"]
    facets:
      task: "nodes/TASK-5.task.md"
      steer: "nodes/TASK-5.steer.md"
    links:
      - target: "CODE-5"
        relation: "produces"
        
  # ... slots 2-4, 6-9
```

---

## 11. Validation Rules

### 11.1 Required Fields
- `cell_id` must match pattern `^[A-Z0-9]{4}-[1-9]$`
- `block` must be exactly 4 characters
- `slot` must be 1-9
- `kind` must be one of the defined enums

### 11.2 Consistency Rules
- `row` and `col` must match the slot formula
- If `kind` is `*_ref`, then `ref` should be non-null
- If `deps` lists a cell_id, that cell must exist in the index

### 11.3 Status Rules
- `blocked` status requires at least one unmet dep OR explicit block
- `done` status should have all `produces` links pointing to existing outputs

---

## 12. Future Extensions

### 12.1 Versioning
Add `version` and `updated_at` fields for change tracking.

### 12.2 Permissions
Add `acl` field for access control in multi-user scenarios.

### 12.3 Computed Fields
Add fields like `completion_pct`, `blocked_by`, `blocking` that are derived at query time.

---

## Appendix A: JSON Schema

See `docs/spec/schemas/cell.schema.json` for the machine-readable JSON Schema definition.

## Appendix B: Changelog

| Version | Date | Changes |
|---------|------|---------|
| v0.1 | 2024-XX-XX | Initial specification |
