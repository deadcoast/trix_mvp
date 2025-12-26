# TRIX Engine v0.1 (geometry-first)

This scaffold proves one thing: **we can keep your ASCII matrix design as the canonical truth** and still have a queryable steering database.

- Geometry is parsed from ASCII skins (prth/clunk/etc.)
- Meaning is attached via mapping (multi-facet nodes)
- Index preserves (row/col/slot) so the matrix stays a spatial system

## Quickstart

```bash
python src/trix_py/tools/trix.py validate examples/blocks/TASK.trix
python src/trix_py/tools/trix.py parse examples/blocks/DOCS.trix
python src/trix_py/tools/trix.py zoom examples/blocks/HUB0.trix --cell 1
python src/trix_py/tools/trix.py context examples/blocks/TASK.trix --cell 5 --repo .
python src/trix_py/tools/trix.py index examples --out examples/.index.json
```

## Where to extend next
- True 9ode/super parsing (3x3 of child matrices).
- Cluster (9x9) derived views.
- Merge/plug operators (mount block into a cell).
- Transforms as first-class nodes (task->code, code->docs).
- Facets as first-class nodes (task->steer, task->config).
- CLI for zooming, context, and next task.

---

Got it. I’m going to stay faithful to your actual TRIX thesis:

- **Geometry is truth** (the ASCII matrices are the primary structure).
- **Skins are just skins** (clunk / prth / fcy / boring are render styles).
- A cell is **not a link** — it’s a **multi‑facet container** (task/doc/code/steer/config/log/etc.).
- The “magic” is your missing layer: **junctions + composition + agent steering** — not markdown formatting.

Below is a full-scope synthesis of what’s already in your repo, what your end-vision implies, the blanks that still need contracts, and a concrete build plan (including code I already wired in so you can actually move).

---

## What you already built (and what it implies)

Your repo already contains **three distinct but compatible layers**:

### 1) Geometry kernel (the real core)

- **`src/geometry_core/spec/TRIX_KERNEL_v0_3.md`** defines the real direction: *geometry-first, multi-facet cells, mount/overlay/splice/transform, hierarchical TRIX addressing*.
- **`src/geometry_core/spec/MATRIX_JUNCTION_v0_2.md`** defines junctions as the mechanism for *composing multiple matrices into one talkable/indexable board with gutters*.

This is the spine of TRIX.

### 2) Two storage “views” (both valid, but you need to choose canonical)

- **`src/trix_py/`** is a geometry-first parser/indexer for **`.trix` + `.map.yaml`** (good for “geometry truth + binding truth”).
- **`src/trix_md/`** is the markdown-y frontmatter approach (good as a *workspace/UI view*, but not canonical if you want to avoid flattening).

These can coexist if you define which one is canonical and which is a view.

### 3) The missing semantic steering layer (your matrix_junction vision)

- **`src/geometry_core/matrix_junction.md`** is NOT just “another spec” — it’s your *semantic control layer*:

  - export vs import nodes using `( )` vs `[ ]`
  - `(+)/(-)` meaning “data emission / placeholder”
  - couplers `|-|-|` meaning “locked/protected anchor”
  - patches `~|~` meaning “workflow/data connection”
  - and your **vlg/hlg gutters** for pinpoint references in a junction canvas

This file is basically “TRIXIE’s control panel grammar.”

---

## The big blanks that still need real contracts

Here are the “fill in the blanks” pieces that TRIX needs to become an actual agentic steering database + PM ecosystem, without collapsing into hyperlinks.

### Blank 1: What is canonical storage?

You have multiple representations. You need **one canonical truth**:

**Recommendation (aligned with your intent):**

- Canonical truth = **`.trix` geometry + `.map.yaml` bindings + facet files**
- Markdown link matrices (`src/trix_md`) = **optional view layer** (human browsing / GitHub-friendly)

This keeps **geometry as truth** and keeps automation deterministic.

### Blank 2: Node identity + facet model

You already implicitly want:

- `node_id` stable identity
- `facets` keyed by facet type
- `meta` for PM semantics (status, deps, priority, etc.)

You need a single schema everyone follows.

**Proposed “minimum stable” node record (binding-level, not UI-level):**

```yaml
node_id: TASK-5
address: TASK#5
meta:
  type: task
  status: active
  priority: 2
  tags: [dispatch, sprint]
  deps: [ARCH#2]
facets:
  task: nodes/TASK-5.task.md
  steer: nodes/TASK-5.steer.md
  log: nodes/TASK-5.log.md
```

Key point: facets are **typed**, not “random files.”

### Blank 3: Composition needs executable semantics

Your kernel lists mount/overlay/splice/transform — but the repo doesn’t yet have the “operator contract” that says:

- **what is allowed to overwrite what**
- how merges are resolved
- where history lives

You already invented the missing safety primitive: **couplers `|-|-|`**.

So the missing contract is basically:

- “automation may write inside regions unless protected by couplers”
- “manual edits always win unless explicitly overridden”
- “every transform writes an event record”

### Blank 4: Junctions need BOTH geometry + semantics

You currently have:

- **junction-as-canvas** (inline ASCII board)
- **junction-as-declaration** (YAML recommended in v0.2)

You also have a third thing:

- **junction-as-semantic steering diagram** (your `matrix_junction.md` assets/operators)

To make this real, you want *two artifacts per junction*:

1. Canonical junction placement (machine truth)
2. Rendered junction board with gutters (human truth)

And then **a semantic overlay** that can annotate regions (vlg/hlg rectangles) with meanings.

### Blank 5: TRIXIE needs a real job protocol

You already wrote the idea in `src/trix_ie/trix_ie.md`:

1. `requirements.trixie`
2. `ma.trixie`
3. `steer.trixie`
4. `trixie`

What’s missing is the I/O contract for each step (what files it reads/writes, what formats, what “done” means).

---

## My concrete read on your end-vision

What you’re actually building is:

### A “steering database” where

- The database is a **generated index**, not a server
- The UI is **ASCII geometry**
- The engine operates by:

  1. parsing geometry
  2. resolving bindings
  3. generating agent context bundles
  4. applying transforms
  5. writing back facets + logs + updated mappings

### A project management ecosystem where

- “Tasks” are a facet type, not a separate tool
- You can run dispatch loops like:

  - choose next task from TASK#4 or TASK#5
  - pull in steering facets from AGNT/DOCS/ARCH
  - execute and write outputs/validation/logs

### A junction system where

- You can say: “the coupler at vlg 06→07, hlg 09→10 locks this anchor”
- You can say: “the patch at vlg 13, hlg 21→23 connects workflows”
  …and a tool can **validate** that those coordinates match the diagram.

That’s not markdown links. That’s a *geometry-addressable control plane*.

---

## Current junction tooling

The geometry-core CLI is now the canonical entry point for junction scanning and gutter-aware validation.
It supports:

- Detecting **multiple embedded 3×3 matrices** in a shared canvas (side-by-side layouts).
- Resolving `(L,C)` or `(vlg/hlg)` coordinates to `TITL#slot` addresses.
- Extracting vlg/hlg regions for operator verification.
- Validating operators against `src/geometry_core/spec/matrix_junction_ops.*`.

### Quick sanity commands

```bash
# scan a junction with multiple matrices in one canvas
python src/geometry_core/tools/trix.py scan src/geometry_core/examples/junctions/matrix_junction_example.md

# resolve a coordinate to a TRIX address (matrix+slot)
python src/geometry_core/tools/trix.py resolve src/geometry_core/examples/junctions/matrix_junction_example.md --lc L0002:C0023
# -> "CODE#5"

# extract a vlg/hlg region from your native-gutter diagram style
python src/geometry_core/tools/trix.py extract src/geometry_core/matrix_junction.md --vlg0 6 --vlg1 7 --hlg0 9 --hlg1 10
# -> shows "|-|-|" region

# validate operator placements using the canonical spec
python src/geometry_core/tools/trix.py validate src/geometry_core/matrix_junction.md --spec src/geometry_core/spec/matrix_junction_ops.yaml

# one-command helper + JSON spec variant
make validate-junction
python src/geometry_core/tools/trix.py validate src/geometry_core/matrix_junction.md --spec src/geometry_core/spec/matrix_junction_ops.json
```

This gives you the first “real steering primitive” you need:
**pinpoint references that resolve into TRIX addresses.**

---

## How to structure the ecosystem so it scales

This is the clean architecture that preserves your vision and makes building feasible.

### Layer 0: Geometry

**Files:**

- `blocks/<TITL>.trix` (geometry)
- `hub/<TITL>.trix` (9ode/super geometry)

**Contract:**

- parser extracts: `titl`, 3×3 tokens, token positions, skin

### Layer 1: Binding

**Files:**

- `blocks/<TITL>.map.yaml`

**Contract:**

- each cell token or slot binds to:

  - `kind: node` + `node_id` + `facets`
  - OR `kind: block/9ode/super` + `ref/path` (mount targets)

This is already in your examples (`examples/maps/*.map.yaml`).

### Layer 2: Junction

**Canonical file (machine):**

- `junctions/<id>.junction.yaml`

**Rendered file (human):**

- `junctions/<id>.junction.md` (ASCII board + gutters)

**Contract:**

- placement list: `(matrix_ref, anchor_line/col, skin)`
- optional connectors: patches/couplers as semantic overlay
- tool can: `(L,C)` → `TITL#slot` via scan index

### Layer 3: Steering engine

**`trixie` doesn’t “own” the truth** — it runs transforms and writes facets.

Recommended job I/O:

#### `requirements.trixie`

Input: user prompt + current index
Output: a structured “requirements map”:

```yaml
inputs:
  u:
    - id: RQ-001
      text: "..."
      tags: [...]
```

#### `ma.trixie`

Input: requirements map + current TRIX state
Output: proposed placements/updates:

```yaml
writes:
  - address: TASK#4
    node_id: TASK-4
    facets:
      task: nodes/TASK-4.task.md
```

#### `steer.trixie`

Input: node candidates
Output: steering facets (constraints, contracts, “don’t break geometry”, etc.)

#### `trixie`

Runs the loop:

- index
- choose next
- context bundle
- apply transform
- write logs

---

## How your import/export grammar fits (without becoming “just syntax”)

From your `matrix_junction.md`:

- **export node** uses parentheses: `( )`
- **import node** uses brackets: `[ ]`
- export data node: `+`
- import data node: `-`
- aliasing: `user -> u`, `trixie -> t`, etc.

This can become an actual executable rule system if you define:

### Rule: export nodes create keys

When you detect `(+)user` in a junction ingest region:

- normalize to alias: `(+u)`
- store: `inputs.u += …`

### Rule: import nodes are obligations

When you detect `[-]` in a target region:

- treat it as “requires fill”
- link it to the nearest patch path
- once filled, it can become `[+]` or `[x]` (whatever you decide) as a completion mark

### Couplers enforce write-protection

If a coupler intersects a region, transforms may not overwrite it.

That’s your guardrail against “agents wrecking the board.”

---

## The next build steps I would drive (in order)

No fluff—this is the shortest path to “real system.”

### Step 1: Unify your canon

Decide in-repo:

- `.trix + .map.yaml` = canonical truth
- `trix_md` = optional view (can be generated from canonical later)

### Step 2: Expand the index

Extend your existing index to include:

- nodes + facets
- matrices + mounts
- junctions + embedded matrix anchors + cell bboxes
- connectors (patches/couplers) as graph edges

### Step 3: Make transforms real

Implement first transform type:

- `task -> code` (writes CODE facet)
- `task -> doc` (writes DOCS facet)
- every transform writes to `logs/` + updates status

### Step 4: Implement TRIXIE job files

Add `/trixie/jobs/*.trixie.yaml` (or `.toml`)

- each job is deterministic I/O
- so agent behavior becomes debuggable and versioned

### Step 5: Render + validate junctions

- renderer: canonical `junction.yaml` → `junction.md` with gutters
- validator: checks that declared placements match what’s in rendered board
- validator: checks coupler regions aren’t overwritten

---

## If you want, I can go even deeper immediately

I can also (in the same “no flattening” spirit):

- design the exact **`.junction.yaml` schema** that matches your vlg/hlg + coupler/patch semantics
- implement an **index unifier** that merges:

  - `trix_py` node facet index
  - `geometry_core` junction embedded-matrix index
- implement the first **transform runner** that respects couplers and writes facets + logs

But the key thing is: we now have a working base primitive:
**a junction scan that can resolve geometry coordinates into TRIX addresses, without converting your world into markdown links.**
