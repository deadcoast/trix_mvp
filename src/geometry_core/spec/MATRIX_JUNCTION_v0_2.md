# Matrix Junction Spec — v0.2

A **Matrix Junction** is a *canvas* that composes multiple TRIX matrices into a bigger view, while preserving:

- where each embedded matrix starts (line/column)
- which skin it uses (optional)
- how to reference an exact location using **gutters**

This is the mechanism that makes large super/cluster views discussable in plain text.

## 1. Canonical vs Display

- Canonical: a junction must be parseable into a list of embedded matrices and their anchors.
- Display: gutters are a *view overlay* that makes coordinates explicit.

You can implement either of these canonical formats:

### A) Inline-canvas junction (parse from ASCII)
The junction is one monospaced ASCII "board" containing multiple block drawings.

Pros: pure ASCII, very TRIX-native  
Cons: parser must detect block boundaries

### B) Declarative junction (recommended canonical)
A YAML/JSON file declares what is placed where, and a renderer generates the ASCII junction.

Pros: deterministic, easy to index, easy to change skins  
Cons: the ASCII file becomes a rendered artifact

Both formats can coexist:
- `matrix_junction.yaml` is canonical
- `matrix_junction.md` is rendered view (with gutters)

## 2. Gutter Overlay

A gutter overlay adds:

- **Vertical gutter**: line numbers on the left
- **Horizontal gutter**: column numbers at the top (optional: tens/hundreds guides)

### Reference format
- `L####` = line index (0-based or 1-based; choose one and stick to it)
- `C####` = column index

Example: `L0042:C0137`

A helper tool should support:
- show gutter overlay
- jump to coordinate
- show what's at that coordinate (which matrix/cell)

## 3. Cell-Level references inside a junction

A coordinate can be lifted into a TRIX address by detecting which embedded matrix region contains it.

Two-step resolution:
1) `(L,C)` → embedded matrix ID (e.g., `[TASK]`) + local coordinate
2) local coordinate → cell slot (1..9) → TRIX address (`TASK#5`)

## 4. Junction Index Record

A junction index entry should record:

- junction_id
- file_path
- embedded_matrices[]:
  - titl
  - skin (if known)
  - anchor: {line, col}
  - bbox: {line0, col0, line1, col1}
  - cells:
    - slot: 1..9
    - approx_center: {line, col}
    - token_bbox: {line0, col0, line1, col1} (optional)

This is what lets agents "pinpoint references" exactly.

## 5. Practical defaults

- Use 0-based `(L,C)` in tools (like editors do internally)
- Render gutters in base10, with a mark every 10 columns
- Normalize tabs to spaces before counting columns
