# Junction revision

## CRITICAL ISSUE REPORT

- GPT FAILED TO ACCESS THE FULL REPO

### What I can see in this environment

I currently only have these files available to open/read:

- `trix.md`
- `matrix_design.md`

I **do not** have the GitHub repo attachment (as a zip/folder) or your new `matrix_junction.md` available on my side in the filesystem right now, so I can’t literally read the new junction spec you described yet.

If you want me to do the true “analyze everything you added” pass, please attach the repo as a `.zip` (or attach `matrix_junction.md` directly). I’m not asking you to re-explain anything — I just need the actual bytes so I can read it.

That said: I **can** (and will) do a full-scope design completion based on the parts I can read, and I’ll define `matrix_junction` + gutters in a way that is consistent with your core TRIX math and your ASCII skins.

---

## 1) The non-negotiables in your core spec (what everything must preserve)

From `trix.md`, these are hard constraints, not implementation details:

- Titles are always encased in `[]`
- Matrices are fundamentally **3-per-row** (your base atomic grouping is 3×3)
- A “matrix box” caps at **9 nodes**
- **ABSOLUTE PURPOSE:** TRIX is a “full scope dispatch ecosystem that steers the project as a whole.”
- Critical modulation feature: blocks must **interact / merge / integrate / transform** and be **plugged in** to other blocks

Your dictionary locks in the **type system**:

- modifiers: `block` (3×3), `cluster` (9×9), `line` (1×3)
- values: `node`, `9ode`, `super`
- design: `hub`, `titl` = strict 4-letter title

So: any tool, DB, agent layer, UI must preserve **geometry-first truth**.

---

## 2) What `matrix_design.md` adds (and what it implies technically)

Your `matrix_design.md` is basically a **rendering + scaling specification**:

### A) You have multiple ASCII “skins”

You define multiple consistent block presentations:

- boring bill / corner finish
- `clunk`
- `prth` (parthanon)
- `fcy` (fancy switchbox)

**Implication:** you need a parser that extracts the same underlying 3×3 logical matrix from many visual skins — without making any skin “canonical”.

### B) You define compounding / zoom levels and larger canvases

You show:

- node, node-line, 3×3 node block
- `9ode` “native representation” as `[9]`
- “superblock” representations (3×3 of `[9]`)
- cluster sized matrices (big grids / condensed variants)

**Implication:** TRIX isn’t just “a block”. It’s a **zoomable fractal workspace**:

- *Zoom changes resolution (node → block → 9ode → super)*
- *Cluster changes extent (more cells at same resolution)*

---

## 3) The real missing “blanks” to reach your end vision

Here are the blanks your system needs to become a real multi-faceted steering database + PM ecosystem — without flattening TRIX into “markdown links”.

### Blank #1: Canonical truth must be geometry + coordinates

TRIX needs a canonical internal representation like:

- matrices have:

  - `shape` (3×3, 1×3, 9×9)
  - `value_type` (node/9ode/super)
  - `skin` (for rendering only)
  - **cell coordinates**

This lets you compute:

- adjacency (neighbors)
- row/col semantics
- zoom mapping (cell contains submatrix)
- junction placement mapping

### Blank #2: A cell is a multi-facet capsule (not a link)

A cell (`node`) must be able to hold multiple “facets” simultaneously:

- `task` facet (checklist/state)
- `doc` facet (spec/narrative)
- `code` facet (path/module pointers)
- `cfg` facet (yaml/toml/json)
- `steer` facet (agent constraints)
- `log/metric` facet

Links can exist, but they are **one facet** among many (not the system).

### Blank #3: “Plug / merge / transform” must be first-class ops

You explicitly require composability.
That means you need explicit operations:

- `mount(target_cell <- matrix_ref)`
- `overlay(A, B)` (merge by coordinate)
- `splice(A.region <- B.region)`
- `transform(inputs -> outputs)` (agent/script/manual)

That’s how TRIX becomes a *workflow engine* instead of a *diagram*.

### Blank #4: `matrix_junction` is the “canvas” layer

Based on your description (new file + gutters), `matrix_junction` is the missing layer that enables:

- large composed views (multi-block / multi-9ode / cluster canvases)
- pinpoint referencing (“look at row 42 col 137”)
- discussion + review in plain text with exact coordinates

This is exactly right — and it shouldn’t be an afterthought.

---

## 4) How I’m defining `matrix_junction` so it matches TRIX (and your gutters)

Even though I can’t read your `matrix_junction.md` yet, the correct TRIX-consistent definition is:

### Matrix Junction

A **matrix junction** is a monospaced ASCII *canvas* that contains many embedded TRIX matrices (blocks/lines/9odes/etc), and provides a way to map:

- **visual coordinates** (line, column)
  → to
- **logical TRIX addresses** (which matrix, which cell)

### Gutters

Guttes are simply a coordinate overlay:

- **Vertical gutter** = line numbers (L####)
- **Horizontal gutter** = column numbers (C####)

This enables exact references like:

- `L0042:C0137`

### Junction resolution pipeline

To resolve a pinpoint reference:

1. `(L,C)` → determine which embedded matrix bounding box contains it
2. within that embedded matrix → determine which cell token `[1]..[9]` is nearest/contains that coordinate
3. return a TRIX address:

   - `TITL#slot` (and if nested: `HUB0#2/TASK#5` style path)

This is the bridge between your **junction example + gutters** and a real **agentic steering DB**.

---

## 5) A concrete tool/kernel that supports junction gutters + scanning (right now)

Since I can’t open your repo attachment yet, I built a **drop-in geometry-first helper pack** that you can merge into your repo immediately.

### Download

[Download trix_geometry_core.zip](sandbox:/mnt/data/trix_geometry_core.zip)

### What it does (no flattening)

- Works on **ASCII skins** (ignores decoration, extracts the 3×3 logical grid)
- Adds a **gutter overlay** (line + column gutters) for pinpoint referencing
- Scans a “junction canvas” file and outputs:

  - which embedded blocks it found
  - their anchor line/col
  - approximate bounding boxes

### Example: gutter overlay output

Running:

```bash
python tools/trix.py gutter examples/junctions/matrix_junction_example.md
```

Produces:

```
     C:0                                                    
     C:0         1         2         3         4         5  
     C:01234567890123456789012345678901234567890123456789012
L0000 ==[TASK]======= ==[CODE]=== =   | ==[DOCS]======= |
L0001 - [1] [2] [3] - | [1] [2] [3] | - | - [1] [2] [3] - |
L0002 - [4] [5] [6] - | [4] [5] [6] | + | - [4] [5] [6] - |
...
```

That is the exact “vertical + horizontal gutter” concept you described — and it’s what allows pinpoint references like `L0002:C0020`.

---

## 6) How this becomes the “agentic steering database + PM ecosystem”

Once you have:

- matrices (geometry),
- junctions (canvas),
- cell facets (multi-faceted data),
- and plug/merge/transform ops,

…the “steering database” is simply an index over those structures.

### The steering DB should store

- all matrices: `titl`, type, level, skin
- all cells: slot, row/col, and **facet bindings**
- all junction placements: anchor coords + cell token coords
- rollups: status summaries for a block / 9ode / super

### Dispatch loop (TRIX-native)

1. start at `hub` (central 9ode)
2. choose block / 9ode by slot
3. within it, choose target cell(s)
4. agent loads facets + neighboring context (spatial + dependency)
5. executes
6. writes outputs/logs facets back into specific cells
7. rollups update at parent level

That’s “steering the project as a whole”, in the way your spec means it.

---

## 7) What I need to do the *real* full-repo analysis you asked for

Right now I can’t see your repo attachment or `matrix_junction.md` contents in the files I can open.

If you attach:

- the repo as `repo.zip` **or**
- `matrix_junction.md` directly

…I will:

- read your new definitions verbatim,
- match the kernel to your exact junction syntax,
- implement the gutter scheme exactly as you designed it,
- produce a complete “spec → parser → index → agent context bundler” plan aligned to your actual repo layout.

No hand-waving, no flattening.

---

If you want one immediate next step that doesn’t require any more back-and-forth:
Attach the repo as a `.zip` and I’ll respond with a **full inventory** (every spec file + every example), a **normalized definition list**, and the **exact missing contracts** needed to make your junction + gutters + compounding work as a coherent system.
