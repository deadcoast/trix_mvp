# TRIX Framework Development Roadmap

## Sequencing Rationale

```
Cell/Facet Schema (B)     ──┐
                            ├──► Composition Layer (A) ──► Agent Protocol (D)
9ode/Super Compounding (C) ─┘
```

**Why this order:**
- B & C are foundation layers — they define *what* cells contain and *how* they compound
- A depends on B (you can't compose cells without knowing their structure)
- D depends on all three (agents navigate compounded structures and read/write cell facets)

---

## Phase 1: Foundation Specs

### [B] Cell/Facet Schema Spec

**Goal:** Define the canonical structure of a TRIX cell as a multi-facet capsule.

#### Spec Outline

```yaml
# CELL_SCHEMA_v0.1.yaml

cell:
  # Identity
  cell_id: string          # format: "{BLOCK}-{slot}" e.g. "TASK-5"
  block: string            # parent block titl (4-char)
  slot: int                # 1..9 position in 3x3
  
  # Coordinates (preserved from geometry)
  row: int                 # 1..3
  col: int                 # 1..3
  
  # Cell classification
  kind: enum               # node | block_ref | 9ode_ref | super_ref | empty
  
  # Facets (the multi-attachment system)
  facets:
    task: path | null      # .task.md
    doc: path | null       # .doc.md
    steer: path | null     # .steer.md (agent constraints)
    code: path | null      # source file reference
    config: path | null    # .yaml/.toml/.json
    log: path | null       # execution history
    metric: path | null    # measurements/KPIs
  
  # Steering metadata
  status: enum             # draft | active | blocked | done | archived
  priority: int | null     # 1 (highest) .. 5 (lowest)
  deps: list[cell_id]      # blocking dependencies
  tags: list[string]       # free-form labels
  owner: string | null     # responsible entity
  
  # Links (cross-references)
  links:
    - target: cell_id
      relation: enum       # requires | produces | extends | see_also
```

#### Spec Deliverables
- [ ] `docs/spec/CELL_SCHEMA_v0.1.md` — narrative spec
- [ ] `docs/spec/schemas/cell.schema.yaml` — machine-readable schema
- [ ] Update `.map.yaml` format to align with schema

---

### [C] 9ode/Super Compounding Spec

**Goal:** Formalize the fractal zoom levels and their navigation semantics.

#### Spec Outline

```yaml
# COMPOUNDING_v0.1.yaml

levels:
  node:
    shape: "1×1"
    contains: data
    titl: null             # nodes don't have titles
    
  block:
    shape: "3×3"
    contains: 9 nodes
    titl: 4-char           # e.g. [TASK], [DOCS]
    slots: 1..9
    
  9ode:
    shape: "3×3 of blocks" # = 9×9 nodes
    contains: 9 blocks
    titl: 4-char           # e.g. [HUB0], [CORE]
    slots: 1..9            # each slot = block ref
    
  super:
    shape: "3×3 of 9odes"  # = 27×27 nodes
    contains: 9 9odes
    titl: 4-char
    slots: 1..9            # each slot = 9ode ref
    
  cluster:
    shape: "9×9"           # derived view, not a container
    view_of: 9ode | super
    purpose: "zoomed-out dashboard"

# Title conventions at each level
titl_prefixes:
  block: null              # any 4-char (TASK, DOCS, CODE)
  9ode: null               # any 4-char (HUB0, CORE)
  super: "S_" | null       # optional prefix for disambiguation

# Navigation
zoom:
  in: "cell.kind == block_ref → load referenced block"
  out: "find parent 9ode/super containing this block"
  
addressing:
  absolute: "{SUPER}#{9ODE}#{BLOCK}#{slot}"  # e.g. "MAIN#HUB0#TASK#5"
  relative: "{BLOCK}#{slot}"                  # e.g. "TASK#5"
```

#### Spec Deliverables
- [ ] `docs/spec/COMPOUNDING_v0.1.md` — narrative spec with visual examples
- [ ] Define title registry/uniqueness rules
- [ ] Define cluster rendering rules (condensed views)

---

## Phase 2: Composition Layer

### [A] Composition Operators Spec

**Goal:** Define the operators that make blocks "plug into" each other.

#### Operator Catalog

```yaml
# COMPOSITION_v0.1.yaml

operators:

  mount:
    signature: "mount(target_cell, matrix_ref) → void"
    effect: "Cell becomes a portal to another matrix"
    example:
      before: "TASK#1 = empty node"
      operation: "mount(TASK#1, DOCS)"
      after: "TASK#1.kind = block_ref, TASK#1.ref = DOCS"
    constraints:
      - target_cell.kind must be empty or block_ref
      - matrix_ref must exist
    
  overlay:
    signature: "overlay(base_matrix, patch_matrix, mode) → matrix"
    effect: "Merge two matrices by coordinate"
    modes:
      - replace: patch overwrites base
      - fill: patch fills empty cells only
      - merge: combine facets (union)
    example:
      base: "TASK with slots 1-4 filled"
      patch: "TEMP with slot 5 filled"
      result: "TASK now has slot 5 from TEMP"
    constraints:
      - shapes must match (3×3 + 3×3)
      - protected regions (couplers) block writes
      
  splice:
    signature: "splice(source.region, target.region) → void"
    effect: "Copy a rectangular region between matrices"
    example:
      source: "DOCS row 1 (slots 1,2,3)"
      target: "TASK row 3 (slots 7,8,9)"
      result: "TASK slots 7,8,9 now mirror DOCS 1,2,3"
    constraints:
      - regions must have same dimensions
      - splice creates references, not copies (unless --deep)
      
  transform:
    signature: "transform(inputs, outputs, method) → void"
    effect: "Workflow primitive: consume inputs, produce outputs"
    methods:
      - manual: human executes
      - agent: AI agent executes
      - script: automation script
    example:
      inputs: [TASK#5]
      outputs: [CODE#5, DOCS#5]
      method: agent
      meaning: "Agent reads TASK#5, writes code and docs"
    constraints:
      - inputs must be readable (status != archived)
      - outputs must be writable (not protected)

  imports:
    signature: "block.imports = [BLOCK_REF, ...]"
    effect: "Context bundler includes steering/decisions from imported blocks"
    example:
      block: TASK
      imports: [AGNT, DOCS, ARCH]
      result: "Agent context for TASK#5 includes AGNT steering + DOCS refs"
```

#### Junction Integration

```yaml
junction_operators:
  # Already defined in matrix_junction.md, but linked here:
  coupler: "protects regions from overlay/splice"
  patch: "connects export→import lanes for data flow"
  export_node: "emits data into junction"
  import_node: "receives data from junction"
```

#### Spec Deliverables
- [ ] `docs/spec/COMPOSITION_v0.1.md` — operator definitions
- [ ] `docs/spec/schemas/operation.schema.yaml` — operation records
- [ ] Update junction spec to reference composition operators

---

## Phase 3: Agent Protocol

### [D] Agent Protocol Spec

**Goal:** Define the contract for how agents interact with the TRIX steering system.

#### Protocol Outline

```yaml
# AGENT_PROTOCOL_v0.1.yaml

# Agent capabilities
agent:
  id: string
  capabilities: list[enum]    # read | write | execute | transform
  
# The steering loop
dispatch_loop:
  
  1_read_hub:
    action: "Load hub 9ode (e.g., HUB0)"
    returns: "9ode structure with block refs"
    
  2_select_block:
    action: "Choose block based on priority/domain"
    heuristic: "TASK for active work, DOCS for references"
    
  3_select_cell:
    action: "Within block, select actionable cell"
    rules:
      - "Prefer slot 5 (Now) over slot 4 (Backlog)"
      - "Skip cells with status = done | archived"
      - "Skip cells with unmet deps"
    returns: "cell_id"
    
  4_build_context:
    action: "Assemble context bundle for selected cell"
    includes:
      - cell: "The target cell with all facets"
      - imports: "Steering/decisions from imported blocks"
      - neighbors: "Adjacent cells (spatial context)"
      - deps: "Dependency chain (what this cell needs)"
    format: "JSON or Markdown bundle"
    
  5_execute:
    action: "Agent performs work"
    reads: "context bundle"
    writes: "artifacts (code, docs, configs)"
    
  6_write_back:
    action: "Update TRIX with results"
    targets:
      - cell.facets: "Add/update output files"
      - cell.status: "Update state (active → done)"
      - slot_7: "Outputs slot"
      - slot_8: "Validation slot"
      - slot_9: "Logs slot"
      
  7_rollup:
    action: "Parent matrices update summaries"
    example: "Block completion % bubbles up to 9ode"

# Context bundle schema
context_bundle:
  target:
    cell_id: string
    block: string
    slot: int
    facets: map[string, content]
  imports:
    - block: string
      cells: list[cell_summary]
  spatial:
    above: cell_id | null
    below: cell_id | null
    left: cell_id | null
    right: cell_id | null
  deps:
    - cell_id: string
      status: enum
      satisfied: bool
```

#### Spec Deliverables
- [ ] `docs/spec/AGENT_PROTOCOL_v0.1.md` — narrative protocol
- [ ] `docs/spec/schemas/context_bundle.schema.yaml`
- [ ] `docs/spec/schemas/dispatch_event.schema.yaml` — for audit logging

---

## Implementation Phases Summary

| Phase | Spec | Depends On | Deliverable |
|-------|------|------------|-------------|
| 1a | Cell/Facet Schema | — | `CELL_SCHEMA_v0.1.md` |
| 1b | Compounding | — | `COMPOUNDING_v0.1.md` |
| 2 | Composition Ops | 1a, 1b | `COMPOSITION_v0.1.md` |
| 3 | Agent Protocol | 1a, 1b, 2 | `AGENT_PROTOCOL_v0.1.md` |

---

## Tracking

### Specification Phase
- [x] Phase 1a: Cell/Facet Schema → `docs/spec/CELL_SCHEMA_v0.1.md`
- [x] Phase 1b: 9ode/Super Compounding → `docs/spec/COMPOUNDING_v0.1.md`
- [x] Phase 2: Composition Operators → `docs/spec/COMPOSITION_v0.1.md`
- [x] Phase 3: Agent Protocol → `docs/spec/AGENT_PROTOCOL_v0.1.md`

### Implementation Phase
- [x] A. Populate trix_md blocks → `src/trix_md/blocks/{TASK,DOCS,CODE,ARCH,AGNT,TEST,DEPL,OPER,META}/`
- [x] B. Create HUB0 9ode → `src/trix_md/hub/HUB0.md`, `HUB0.map.yaml`
- [x] C. Reference implementations → `src/trix_py/lib/{bundler,dispatch}.py`, CLI commands
- [x] D. Slot semantics spec → `docs/spec/SLOT_SEMANTICS_v0.1.md`, `schemas/slot_semantics.schema.yaml`

