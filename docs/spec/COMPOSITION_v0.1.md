# TRIX Composition Operators Specification v0.1

> **Status:** Draft  
> **Depends:** Cell Schema v0.1, Compounding v0.1  
> **Enables:** Agent Protocol

---

## 1. Purpose

This specification defines the **operators** that make TRIX blocks "plug into" each other. These are the contracts for composition, transformation, and data flow between matrices.

The goal is to move TRIX from static diagrams to a **dynamic workflow system** where blocks can be mounted, merged, spliced, and transformed.

---

## 2. Core Principles

### 2.1 Geometry is Immutable
Operators modify **bindings and content**, never geometry. A 3×3 block remains 3×3.

### 2.2 Operations are Explicit
No implicit merges or hidden transforms. Every composition is a recorded operation.

### 2.3 Regions Can Be Protected
Couplers and locks prevent operators from modifying critical zones.

### 2.4 Reversibility
Where possible, operations are reversible or logged for audit.

---

## 3. Operator Catalog

### 3.1 Overview

| Operator | Signature | Effect |
|----------|-----------|--------|
| `mount` | `mount(target, ref)` | Cell becomes portal to another matrix |
| `unmount` | `unmount(target)` | Remove portal, cell becomes empty |
| `overlay` | `overlay(base, patch, mode)` | Merge two matrices by coordinate |
| `splice` | `splice(src.region, dst.region)` | Copy rectangular region between matrices |
| `transform` | `transform(inputs, outputs, method)` | Workflow: consume inputs, produce outputs |
| `imports` | `block.imports = [...]` | Context composition (automatic bundling) |
| `link` | `link(source, target, relation)` | Create typed relationship |
| `protect` | `protect(region)` | Mark region as immutable |

---

## 4. Mount / Unmount

### 4.1 Mount

Makes a cell a portal to another matrix (block, 9ode, or super).

```yaml
operator: mount
signature: "mount(target_cell: cell_id, ref: titl, path?: string) → void"

preconditions:
  - target_cell.kind in [empty, block_ref, 9ode_ref, super_ref]
  - ref must exist or path must be valid

postconditions:
  - target_cell.kind = block_ref | 9ode_ref | super_ref
  - target_cell.ref = ref
  - target_cell.path = path (if provided)
```

**Example:**
```yaml
# Before
TASK-1:
  kind: empty
  
# Operation
mount(TASK-1, "DOCS", "blocks/DOCS.trix")

# After
TASK-1:
  kind: block_ref
  ref: "DOCS"
  path: "blocks/DOCS.trix"
```

**Use case:** Hub 9ode mounts domain blocks into its slots.

### 4.2 Unmount

Removes a portal, returning cell to empty.

```yaml
operator: unmount
signature: "unmount(target_cell: cell_id) → void"

preconditions:
  - target_cell.kind in [block_ref, 9ode_ref, super_ref]

postconditions:
  - target_cell.kind = empty
  - target_cell.ref = null
  - target_cell.path = null
```

**Note:** This does NOT delete the referenced matrix, only the link.

---

## 5. Overlay

Merges two matrices by coordinate position.

```yaml
operator: overlay
signature: "overlay(base: titl, patch: titl, mode: overlay_mode) → titl"

modes:
  replace: "Patch cells overwrite base cells"
  fill: "Patch cells fill empty base cells only"
  merge: "Combine facets (union)"
  deep_merge: "Recursively merge facet content"
```

### 5.1 Overlay Modes

**Replace Mode:**
```
Base:              Patch:             Result:
┌───┬───┬───┐     ┌───┬───┬───┐     ┌───┬───┬───┐
│ A │ B │ C │  +  │   │ X │   │  =  │ A │ X │ C │
├───┼───┼───┤     ├───┼───┼───┤     ├───┼───┼───┤
│ D │ E │ F │     │   │ Y │   │     │ D │ Y │ F │
├───┼───┼───┤     ├───┼───┼───┤     ├───┼───┼───┤
│ G │ H │ I │     │   │   │   │     │ G │ H │ I │
└───┴───┴───┘     └───┴───┴───┘     └───┴───┴───┘
```
Patch slot 2 and 5 have content; they replace base slots 2 and 5.

**Fill Mode:**
```
Base:              Patch:             Result:
┌───┬───┬───┐     ┌───┬───┬───┐     ┌───┬───┬───┐
│ A │   │ C │  +  │ X │ Y │ Z │  =  │ A │ Y │ C │
├───┼───┼───┤     ├───┼───┼───┤     ├───┼───┼───┤
│   │ E │   │     │ P │ Q │ R │     │ P │ E │ R │
├───┼───┼───┤     ├───┼───┼───┤     ├───┼───┼───┤
│ G │   │ I │     │   │   │   │     │ G │   │ I │
└───┴───┴───┘     └───┴───┴───┘     └───┴───┴───┘
```
Patch fills only empty cells in base.

**Merge Mode:**
```yaml
# Base cell
TASK-5:
  facets:
    task: "task.md"
    doc: null

# Patch cell  
PATCH-5:
  facets:
    doc: "doc.md"
    steer: "steer.md"

# Result (merged)
TASK-5:
  facets:
    task: "task.md"    # from base
    doc: "doc.md"      # from patch
    steer: "steer.md"  # from patch
```

### 5.2 Overlay Constraints

- Shapes must match (3×3 overlay onto 3×3)
- Protected regions (couplers) block writes
- Returns a new matrix or modifies base in-place (configurable)

### 5.3 Overlay Schema

```yaml
operation:
  type: overlay
  base: "TASK"
  patch: "HOTFIX"
  mode: "fill"
  in_place: false        # true = modify base; false = create new
  result: "TASK_v2"      # output matrix name (if not in_place)
  protected:
    - slot: 5            # don't overwrite slot 5
```

---

## 6. Splice

Copies a rectangular region from one matrix to another.

```yaml
operator: splice
signature: "splice(source: region, target: region, mode: splice_mode) → void"

region: 
  matrix: titl
  slots: list[int]    # e.g., [1, 2, 3] for row 1
  # OR
  rows: range         # e.g., 1..1 (row 1)
  cols: range         # e.g., 1..3 (all columns)
```

### 6.1 Splice Example

Copy row 1 of DOCS to row 3 of TASK:

```yaml
operation:
  type: splice
  source:
    matrix: "DOCS"
    slots: [1, 2, 3]     # row 1
  target:
    matrix: "TASK"
    slots: [7, 8, 9]     # row 3
  mode: reference        # or "copy"
```

**Reference mode:** Target slots become refs to source cells.  
**Copy mode:** Target slots get deep copies of source content.

### 6.2 Splice Shapes

Spliced regions must have matching dimensions:

| Source | Target | Valid |
|--------|--------|-------|
| 1×3 (row) | 1×3 (row) | ✓ |
| 3×1 (column) | 3×1 (column) | ✓ |
| 2×2 (quad) | 2×2 (quad) | ✓ |
| 1×3 | 3×1 | ✗ (mismatch) |

### 6.3 Splice Constraints

- Protected slots reject writes
- Source must be readable
- Target must be writable

---

## 7. Transform

A workflow primitive that consumes inputs and produces outputs.

```yaml
operator: transform
signature: "transform(inputs: list[cell_id], outputs: list[cell_id], method: transform_method) → void"

methods:
  manual: "Human performs the work"
  agent: "AI agent executes"
  script: "Automation script runs"
  template: "Template expansion"
```

### 7.1 Transform Schema

```yaml
operation:
  type: transform
  name: "spec_to_code"
  inputs:
    - "TASK-5"           # task definition
    - "ARCH-2"           # architecture constraints
  outputs:
    - "CODE-5"           # generated code
    - "DOCS-5"           # generated docs
  method: agent
  agent_id: "codegen-v1"
  constraints:
    - "Follow style guide"
    - "Include tests"
```

### 7.2 Transform Lifecycle

```
┌─────────┐     ┌───────────┐     ┌─────────┐
│ PENDING │ ──► │ EXECUTING │ ──► │ COMPLETE│
└─────────┘     └───────────┘     └─────────┘
                      │
                      ▼
                ┌─────────┐
                │ FAILED  │
                └─────────┘
```

### 7.3 Transform Record

After execution, a transform leaves a record:

```yaml
transform_record:
  id: "txfm_001"
  name: "spec_to_code"
  started_at: "2024-01-15T10:00:00Z"
  completed_at: "2024-01-15T10:05:23Z"
  status: "complete"
  inputs:
    - cell_id: "TASK-5"
      snapshot: "hash:abc123"      # content at execution time
  outputs:
    - cell_id: "CODE-5"
      facets_written: ["code"]
  executor:
    method: "agent"
    agent_id: "codegen-v1"
  logs: "transforms/txfm_001.log"
```

---

## 8. Imports

Declarative composition for context bundling.

```yaml
operator: imports
location: block front matter
effect: "Context bundler includes steering/decisions from imported blocks"
```

### 8.1 Import Declaration

In the block's map file:

```yaml
# TASK.map.yaml
titl: "TASK"
kind: "block"

imports:
  - "AGNT"    # agent steering
  - "ARCH"    # architecture decisions
  - "DOCS"    # documentation references
```

### 8.2 Import Resolution

When building context for `TASK-5`, the bundler:

1. Loads `TASK-5` cell with all facets
2. For each imported block (`AGNT`, `ARCH`, `DOCS`):
   - Loads cells with `steer` or `doc` facets
   - Includes them in the context bundle
3. Returns unified context

### 8.3 Import Semantics

| Import Type | What Gets Included |
|-------------|-------------------|
| Block name | All cells with `steer` or `doc` facets |
| `BLOCK:slot` | Specific cell only |
| `BLOCK:facet` | All cells, but only that facet type |

**Examples:**
```yaml
imports:
  - "AGNT"           # all steering from AGNT
  - "ARCH:6"         # only ARCH-6 (decisions slot)
  - "DOCS:doc"       # all doc facets from DOCS
```

---

## 9. Link

Creates typed relationships between cells.

```yaml
operator: link
signature: "link(source: cell_id, target: cell_id, relation: relation_type) → void"

relation_types:
  requires: "Source needs target to function"
  produces: "Source generates target"
  extends: "Source builds upon target"
  see_also: "Related reference"
  blocks: "Source prevents target from starting"
```

### 9.1 Link Examples

```yaml
# TASK-5 produces CODE-5 and DOCS-5
link(TASK-5, CODE-5, produces)
link(TASK-5, DOCS-5, produces)

# CODE-5 requires ARCH-2
link(CODE-5, ARCH-2, requires)

# TASK-6 is blocked by TASK-5
link(TASK-5, TASK-6, blocks)
```

### 9.2 Link Effects

| Relation | Effect on Target |
|----------|------------------|
| `requires` | Target must be `done` before source can start |
| `produces` | Target is expected output of source |
| `blocks` | Target cannot start until source is `done` |

---

## 10. Protect

Marks a region as immutable.

```yaml
operator: protect
signature: "protect(region: slots | matrix) → void"
effect: "Subsequent mount/overlay/splice/transform cannot write to protected region"
```

### 10.1 Protection Levels

| Level | Scope | Example |
|-------|-------|---------|
| `cell` | Single slot | `protect(TASK-5)` |
| `row` | Slots 1-3, 4-6, or 7-9 | `protect(TASK:[1,2,3])` |
| `column` | Slots 1-4-7, 2-5-8, or 3-6-9 | `protect(TASK:[1,4,7])` |
| `matrix` | All 9 slots | `protect(TASK:*)` |

### 10.2 Protection in Junctions

In junction canvases, **couplers** (`-|-`) mark protected spans:

```
|-|-|-----|%|-----|-|-|
```

This is visual protection. The operator form is:

```yaml
protect:
  matrix: "TASK"
  junction_span:
    vlg: 12
    hlg: [9, 10]
  locked: true
```

### 10.3 Unprotect

```yaml
operator: unprotect
signature: "unprotect(region) → void"
precondition: caller has authority to modify protection
```

---

## 11. Junction Operators

These operators are defined in `matrix_junction.md` and integrated here for completeness.

### 11.1 Coupler

```yaml
operator: coupler
symbol: "-|-"
effect: "Locks junction span; transforms cannot overwrite"
junction_only: true
```

### 11.2 Patch

```yaml
operator: patch
symbol: "~"
effect: "Connects export lane to import lane"
junction_only: true
```

### 11.3 Export Node

```yaml
operator: export_node
symbol: "(+)"
effect: "Emits data into junction"
creates: "<parent>.input.<alias>"
```

### 11.4 Import Node

```yaml
operator: import_node
symbol: "[-]"
effect: "Receives data from junction"
creates: "<parent>.req.<label>"
```

---

## 12. Operation Records

All operations are logged for audit and reversibility.

### 12.1 Record Schema

```yaml
operation_record:
  id: string              # unique operation ID
  type: enum              # mount | overlay | splice | transform | ...
  timestamp: datetime
  actor: string           # user or agent ID
  parameters: object      # operation-specific params
  result: enum            # success | failure | partial
  error: string | null
  before_state: snapshot  # optional, for reversibility
  after_state: snapshot   # optional
```

### 12.2 Operation Log

```
.trix/
└── operations/
    ├── 2024-01-15/
    │   ├── op_001_mount.yaml
    │   ├── op_002_transform.yaml
    │   └── op_003_overlay.yaml
    └── index.yaml
```

---

## 13. Composition Patterns

### 13.1 Template Blocks

A block designed to be overlaid onto others:

```yaml
# TMPL.map.yaml
titl: "TMPL"
kind: "template"
purpose: "Standard slot semantics"

cells:
  "1": { facets: { doc: "Charter template" } }
  "5": { facets: { task: "Now slot template" } }
  "9": { facets: { log: "Logs template" } }
```

**Usage:** `overlay(NEW_BLOCK, TMPL, fill)`

### 13.2 Pipeline Composition

Chain of transforms:

```yaml
pipeline:
  - transform(TASK-5, SPEC-5, agent)
  - transform(SPEC-5, CODE-5, agent)
  - transform(CODE-5, TEST-5, agent)
  - transform([CODE-5, TEST-5], DOCS-5, agent)
```

### 13.3 Mirror Blocks

Blocks that splice from each other to stay in sync:

```yaml
mirror:
  source: "PROD/TASK"
  target: "STAGE/TASK"
  mode: "reference"
  sync: "on_change"
```

---

## 14. Error Handling

### 14.1 Common Errors

| Error | Cause | Recovery |
|-------|-------|----------|
| `PROTECTED_REGION` | Write to protected slot | Remove protection or choose different target |
| `SHAPE_MISMATCH` | Overlay/splice dimension mismatch | Ensure regions have same shape |
| `REF_NOT_FOUND` | Mount to non-existent matrix | Create matrix or fix ref |
| `CYCLE_DETECTED` | Circular mount chain | Break the cycle |
| `DEPS_UNMET` | Transform inputs not ready | Wait for deps to complete |

### 14.2 Rollback

Operations support rollback when `before_state` is captured:

```yaml
rollback:
  operation_id: "op_002"
  restore_from: "before_state"
```

---

## 15. Validation Rules

### 15.1 Pre-Operation Checks

- **mount:** Target exists, ref exists, no cycles
- **overlay:** Shapes match, no protected conflicts
- **splice:** Shapes match, source readable, target writable
- **transform:** Inputs exist and are readable, outputs writable

### 15.2 Post-Operation Checks

- All cell_ids remain valid
- No orphaned references
- Protected regions unchanged

---

## Appendix A: Operator Quick Reference

```
MOUNT       mount(cell, ref)              Cell → Portal
UNMOUNT     unmount(cell)                 Portal → Empty
OVERLAY     overlay(base, patch, mode)    Merge matrices
SPLICE      splice(src, dst)              Copy region
TRANSFORM   transform(in, out, method)    Workflow execution
IMPORTS     block.imports = [...]         Context composition
LINK        link(src, dst, relation)      Create relationship
PROTECT     protect(region)               Lock region
```

---

## Appendix B: Changelog

| Version | Date | Changes |
|---------|------|---------|
| v0.1 | 2024-XX-XX | Initial specification |
