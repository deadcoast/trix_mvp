# TRIX Kernel v0.2

> Legacy draft. Current specs live in `src/geometry_core/spec/TRIX_KERNEL_v0_3.md` and
> `src/geometry_core/spec/MATRIX_JUNCTION_v0_2.md`. CLI paths below match the repo layout.

# TRIX Engine Kernel v0.1 (geometry-first)

This kernel is **not** "a bunch of markdown links".
It treats your ASCII matrix geometry as the **primary structure** and everything else (docs, tasks, code, steering) as **facets attached to cells**.

Your docs define:
- Titles are encased in square brackets `[]`.
- Base **block** is 3x3 (9 cells).
- Higher order: **9ode** (3x3 of blocks), **super** (3x3 of 9odes), and **cluster** (9x9 view/representation).
- Blocks must be able to **plug in / merge / transform** other blocks.

This engine does three things:
1) Parse **your ASCII matrix skins** into a canonical AST (cells + coordinates).
2) Resolve each cell to a **multi-faceted record** (task/doc/code/config/steer/etc.) via mapping.
3) Provide a zoomable API (CLI for now) to navigate block -> 9ode -> super, and to build "agent context bundles".

## File types

### `.trix` : geometry (ASCII)
A `.trix` file contains the ASCII matrix (any skin), e.g. Parthanon:

```
==[TASK]=======
- [1] [2] [3] -
- [4] [5] [6] -
- [7] [8] [9] -
===============
```

The parser extracts:
- `titl`: `TASK`
- `cells`: 3 rows x 3 cols of raw cell tokens

### `.map.yaml` : meaning (multi-facet binding)
A mapping binds each cell token to either:
- a node record (multi-facet payload), or
- a child matrix (plug-in / zoom target)

Example (cell "5" is a node with multiple facets):
```yaml
cells:
  "5":
    kind: node
    node_id: TASK-5
    facets:
      task: examples/nodes/TASK-5.task.md
      steer: examples/nodes/TASK-5.steer.md
```

Example (cell "1" in hub plugs in another block):
```yaml
cells:
  "1":
    kind: block
    ref: DOCS
    path: examples/blocks/DOCS.trix
```

## CLI
- `python src/trix_py/tools/trix.py parse examples/blocks/TASK.trix`
- `python src/trix_py/tools/trix.py validate examples/blocks/TASK.trix`
- `python src/trix_py/tools/trix.py zoom examples/blocks/HUB0.trix --cell 1`
- `python src/trix_py/tools/trix.py context examples/blocks/TASK.trix --cell 5 --repo .`
- `python src/trix_py/tools/trix.py index examples --out examples/.index.json`

## Where to extend next
<!--
- A **3×3 block** is the atomic “module” of work/knowledge (`block` / `bk`).
- A **9ode** is a higher-order module made of blocks (`9ode` / `9o`).
- A **super** is a 3×3 of 9odes (`super` / `su`).
- A **cluster** is a 9×9 “zoomed out” view (`cluster` / `cl`).
- Everything is constrained by **3-per-row**, **9 total cells**, and **strict bracketed titles** with **4-char `titl`**.
- The whole purpose is **agentic dispatch + steering across docs/code/tasks/configs** — the matrix is the “missing unifier.”
- The different ASCII “skins” (boring bill / clunk / parthanon / fancy) are *representations*, not the underlying system.

So the real problem isn’t “how do I draw matrices.”
It’s: **what are the missing contracts that turn the matrices into a real steering database + PM ecosystem?**
-->
---

## The missing pieces that make TRIX “real”

### 1) Canonical storage vs visual skins

Your docs show multiple matrix formats and “skins.”
That’s great visually, but agents/tools need **one canonical parseable format**.

**Blank to fill:** *What’s the canonical format?*
**Answer (recommended):**

- **Canonical = markdown-table rows starting with `|` containing links** (machine-readable).
- **Skins = render layer only** (optional, human-only).

This keeps your aesthetic freedom *and* makes automation deterministic.

---

### 2) Node schema (what a node “is” in the database)

Right now, a “node” is conceptually a unit of data, but you need it to be a **queryable record**.

**Blank to fill:** *What fields must every node have?*
**Answer (recommended minimum):**

- `node_id`: stable ID (`TASK-5`)
- `block`: owning block (`TASK`)
- `slot`: 1–9
- `type`: task/doc/steering/decision/code/config/log/metric/link
- `status`: draft/active/blocked/done/archived
- optional but high-leverage: `priority`, `deps`, `tags`, `links`, `owner`

This is what turns “markdown files” into a real “steering database.”

---

### 3) Slot semantics (so agents don’t guess what [6] means)

Your rules lock shape (3×3), but not meaning.
Agents do better when slots have consistent semantics.

**Blank to fill:** *What do slots 1–9 mean?*
**Answer (recommended default mapping):**

1. Charter
2. Inputs
3. References
4. Backlog
5. Now
6. Decisions
7. Outputs
8. Validation
9. Logs

This becomes the “operating language” of trix.

---

### 4) “Plug-in” / “merge” / “transform” needs an explicit mechanism

You require blocks to *interact, merge, integrate, transform, plug in.*
That’s the defining feature — but it needs a concrete mechanism.

**Blank to fill:** *How does a block plug into another block?*
**Answer (recommended v0 mechanism): `imports`**

- A block declares in its `matrix.md` front matter:

```yaml
imports: [AGNT, DOCS, ARCH]
```

Then any “agent context bundle” for nodes in that block automatically includes:

- the node itself
- its direct `links:`
- steering/decision nodes from imported blocks

That is *real* composability without needing a big engine yet.

---

### 5) The “agentic steering loop” needs a contract too

You said “agenticly coordinates and steers.”
So agents need a standardized loop:

**Blank to fill:** *What is the agent protocol?*
**Answer (recommended):**

1. Read hub (`HUB0`)
2. Go to `TASK-5 (Now)` then `TASK-4 (Backlog)`
3. Build context for the chosen node (includes imported steering/decisions)
4. Execute work
5. Write back into:

   - outputs (slot 7)
   - validation (slot 8)
   - logs (slot 9)
6. Update status/priority/deps

That’s how the system “steers” instead of just “stores.”

---

## What I built to move you toward that end vision (right now)

I took your MVP and filled in the missing “kernel contracts”:

- Added a **kernel spec doc** (v0.1)
- Added **JSON schemas** for node + matrix front matter
- Added **default slot semantics**
- Implemented **block `imports`** as the first “plug-in/merge” mechanism
- Added new CLI commands:

  - `context` → output a quick JSON bundle for a cell in a `.trix` block
  - `bundle` → build Agent Protocol bundles from `src/trix_md`
  - `dispatch` → select the next actionable cell (Agent Protocol)
- Updated `TASK` to import `AGNT`, `DOCS`, `ARCH` so context automatically pulls steering + decisions

Legacy zip reference (archived; use repo commands below):

[Download trix_kernel_v0_2.zip](sandbox:/mnt/data/trix_kernel_v0_2.zip)

Example usage in this repo:

```bash
python src/trix_md/tools/trix.py validate --repo src/trix_md
python src/trix_md/tools/trix.py index --repo src/trix_md
python src/trix_py/tools/trix.py bundle TASK-5 --trix-root src/trix_md --format markdown
python src/trix_py/tools/trix.py dispatch --trix-root src/trix_md --blocks TASK --json
```

---

## The “end-state architecture” (so you know where we’re driving)

Think of TRIX as 4 layers:

### Layer 1 — Matrix UI (human navigation)

- `matrix.md` files are dashboards
- links point to node files (or code/config/docs)
- skins are render-only

### Layer 2 — Steering Database (machine truth)

- generated index (JSON now, SQLite later if you want)
- queryable: “what’s active?”, “what’s blocked?”, “what depends on ARCH-2?”

### Layer 3 — Composition + Transform

- `imports` = composition (context merge)
- later: `exports` + `mount` mappings + transformations (“TASK → CODE plan”, “CODE → DOCS updates”)

### Layer 4 — Agent Protocol + Dispatch

- dispatcher selects next actionable node
- context bundler pulls correct steering/decisions
- agents execute and write back

This exactly matches your “dispatch ecosystem that steers the project as a whole.”

---

## If you want me to “fill blanks” even harder (next logical expansions)

Without asking you a bunch of questions, these are the highest-value blanks to define next:

### A) A real dependency model

Add to nodes:

- `deps: [ARCH-2, DOCS-6]`
- dispatcher rule: only choose tasks whose deps are `done`

### B) A real “transform” concept

Introduce node type: `transform`

- A transform node specifies:

  - inputs (node_ids)
  - outputs (node_ids)
  - method (manual/agent/script)
- This turns “plugging/transforming” into a first-class workflow primitive.

### C) Cluster / superblock navigation

You already defined the compounding and the display patterns.
Next: formalize *navigation semantics*:

- `super` is the portfolio map
- each `9ode` is a domain (product/engineering/ops/etc.)
- each block is a module inside that domain

### D) An event log (so it becomes a true management ecosystem)

Add `trix/events/*.jsonl` as append-only history:

- who changed what node
- what status moved
- what outputs were created

This makes it auditable and automation-friendly.

---

## Quick check: the one thing I’m assuming about your end vision

I’m assuming your “truth source” is **repo-native + Git-friendly**:

- nodes are markdown
- matrices are markdown
- the “database” is generated (index)

That aligns with your examples linking to markdown/configs/code/steering files.

If your end vision instead includes a **running server + UI**, we can still do it — but the *kernel* above stays the same (it’s just the backend contract).

---
<!--
If you want, tell me what you consider the *top 3 blocks that must feel magical* (TASK? AGNT? CODE? DOCS? OPER?), and I’ll propose the exact slot-by-slot semantics + transforms for those blocks so the system starts “steering” immediately instead of being a static map. 
-->
