# Matrix Junction

## Related Files

[overview.md](src/geometry_core/overview.md)
[MATRIX_JUNCTION_V02](src/geometry_core/spec/MATRIX_JUNCTION_v0_2.md)
[TRIX_KERNEL_V03](src/geometry_core/spec/TRIX_KERNEL_v0_3.md)
[GEOMETRY CORE EXAMPLES][src/geometry_core/examples/blocks]
  [CODE.trix][src/geometry_core/examples/blocks/CODE.trix]
  [DOCS.trix][src/geometry_core/examples/blocks/DOCS.trix]
  [TASK.trix][src/geometry_core/examples/blocks/TASK.trix]
[trix_md](src/geometry_core/trix_md)
  [NodeBlockDirectory][src/geometry_core/trix_md/blocks]
  [NodeHubDirectory][src/geometry_core/trix_md/hub]
  [NodeSpectDirectory][src/geometry_core/trix_md/spec]

### `matrix_junction` design

Reference dictionary for the junction grammar and alias normalization. This is
used to read and render junction canvases consistently.

```toml
[agent]
agent.trix = "trixie"

[trixie]
trixie.agents = "trixie"
trixie.req = "requirements"
trixie.steer = "steering"

[map]
map.alias = "m"

[matrix]
matrix.alias = "ma"

[data]

[node]
export.node.brackets = "( )"
export.data.node = "+"
import.node.brackets = "[ ]"
import.data.node = "-"

[trixmap]


[alias]
trixie.alias = "t"
user.alias = "u"
[user]

[user.req]
[user.input]

```

```yaml
R001:
  rule: "Export nodes create input keys using the parent alias."
  example: "(+)user -> (+u) => user.input.u"
  form: "(+)<alias>"
R002:
  rule: "Couplers lock a junction span; transforms must not overwrite protected regions."
  example: "|-|-| at vlg 06-07, hlg 09-10"
  form: "-|-"
R003:
  rule: "Patches are data conduits; connect export lanes to import lanes along the patch."
  example: "~|~ bridging user -> trixie"
  form: "~"
R004:
  rule: "Import nodes register requirements under the parent alias."
  example: "[-]req -> trixie.req"
  form: "[-]<label>"
R005:
  rule: "Export data markers '+' indicate emission lanes in a node or matrix row."
  example: "(+)req or | + |"
  form: "+"
R006:
  rule: "Import data markers '-' indicate required lanes in a node or matrix row."
  example: "[-] or | - |"
  form: "-"
R007:
  rule: "Junction ports are neutral connection anchors and do not resolve to numeric slots."
  example: "[| |] between two frames"
  form: "[| |]"
R008:
  rule: "Matrix bridge ports ([//]) indicate a matrix-level connection using the matrix alias prefix."
  example: "ma.trixie under [//]"
  form: "[//]"
R009:
  rule: "Matrix core markers (%) are structural anchors for centering; they carry no data payload."
  example: "|-----|%|-----|"
  form: "%"
R010:
  rule: "Alias normalization uses [alias] mappings; if none exist, use the literal label as the key."
  example: "user -> u; unknown stays 'unknown'"
  form: "<label>"
R011:
  rule: "Alias prefixes reserve namespaces for matrix and map references."
  example: "ma.trixie (matrix), m.task (map)"
  form: "ma.<alias>, m.<alias>"

```

### Junction parse flow (v0)

1) Load the alias table from `[alias]`.
2) Detect export/import nodes and normalize their parent labels via aliases.
3) Record patches as connections between export and import lanes.
4) Record couplers as protected spans that transforms must not overwrite.
5) Collect ports (`[| |]`, `[//]`) as connection anchors between frames.

### Layout-only marks

- `border`, `sub_border`, and the gutter lines are visual frames; they are not operators.
- `%` is structural (center/anchor) and does not create bindings.

> sub_border
```yaml
----------------- 
|               |
----------------- 
```

## Matrix Junctions

> Matrix 1:1 Node Grid 3x3
- The following example is designed so you can see all aspects in how the junctions integrate into the matrix

- Line Border Gutters: "Example below will use `vlg`, `hlg` for coordinates in explanations"
  - `matrix_junction`, `trix_junct`: The matrix housing blocks
  - `vertical_line_gutter`, `vlg`: left-side row labels
  - `horizontal_line_gutter`, `hlg`: bottom row column labels
  - `coordinates`, `coord`: coordinates to reference specific assets in the `trix_junct`
  - `operator`: if applicable, a character the asset uses to represent itself in the matrix
  - `tag`: a `RuleID` for the asset `R` plus three numbers `000` = `R000`
  - `description`
  - `example`, `eg`

> Matrix Junction
```yaml
+--+-----------------------------------------------------------------+--+
+--+-----------------------------------------------------------------+--+
|17|                                                                 |  |
|16|   |---|-----|%|-----|---|             |---|-----|%|-----|---|   |  |
|15|   | - |     + -     | + |             | - |     + -     | + |   |  |
|14|   |---|   matrix    |---|             |---|   matrix    |---|   |  |
|13|   | + |     - +     | - |             | + |     - +     | -~|~  |  |
|12|   |---|-----|%|-----|-|-|             |-|-|-----|%|-----|---|   |  |
|11|                     |-|-|-----|%|-----|-|-|                     |  |
|10|                     | - |     + -     | + |                     |  |
|09|                     |---|   matrix    |---|                     |  |
|08|                    ~|~+ |     - +     | - |                     |  |
|07|                     |-|-|-----|%|-----|-|-|                     |  |
|06|                     |-|-|-----|%|-----|-|-|                     |  |
|05|                     | - |     + -     | + |                     |  |
|04|                     |---|   matrix    |---|                     |  |
|03|                     | + |     - +     | - |                     |  |
|02|                     |---|-----|%|-----|---|                     |  |
|01|                                                                 |  |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|01|02|03|04|05|06|07|08|09|10|11|12|13|14|15|16|17|18|19|20|21|21|23|24|
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
```

> `trix_junct` Definition Template:
```md
---
### [0]
- `ID`: the name of the asset
  - `tag`: `R000` format
- `operator`: exact glyph or token used in the junction
- `eg`: real example of the asset from the junction canvas
  - `coord` (optional if the example is in a guttered junction)
    - `vlg`
    - `hlg`
```

```yaml
ID:
tag:
operator:
example:
  coord: # optional for guttered junctions
    - vlg:
    - hlg:
```

---
### [1]
- `coupler`, `-|-`: locks a junction span so nodes cannot be overwritten or moved by transforms.

```yaml
# Direct Example
ID: coupler
tag: R002
operator: "-|-"
example: "|-|-|"
coord:
  - vlg: 06->07
  - hlg: 09->10
```

---
### [2]
- `patch`, `~`: connects data workflows between nodes across a junction.

```yaml
# Direct Example
ID: patch
tag: R003
operator: "~"
example: "~|~"
coord:
  - vlg: 13
  - hlg: 21->23
```

---
### [3]
- `export_node`, `( )`: a node that emits data into the junction.
  - Parent alias is the nearest node label (for example `[user]` or `[trixie]`).
  - Export nodes are normalized via `[alias]` and stored in `<alias>.input`.

```yaml
# Direct Example
ID: export_node
tag: R001
operator: "( )"
example: "(+)user"
coord:
  - vlg: "n/a (see minimal_matrix)"
  - hlg: "n/a (see minimal_matrix)"
```

---
### [4]
- `import_node`, `[ ]`: a node placeholder that requests data from the junction.
  - Import nodes register requirements under `<alias>.req` until resolved.

```yaml
# Direct Example
ID: import_node
tag: R004
operator: "[ ]"
example: "[-]req"
coord:
  - vlg: "n/a (see minimal_matrix)"
  - hlg: "n/a (see minimal_matrix)"
```

---
### [5]
- `export_data`, `+`: data emission marker inside a node or matrix row.
  - Used in `fcy` rows and inside export nodes like `(+)req`.

```yaml
# Direct Example
ID: export_data
tag: R005
operator: "+"
example: "| + |"
coord:
  - vlg: "see Matrix Junction example"
  - hlg: "see Matrix Junction example"
```

---
### [6]
- `import_data`, `-`: data requirement marker inside a node or matrix row.
  - Used in `fcy` rows and inside import nodes like `[-]`.

```yaml
# Direct Example
ID: import_data
tag: R006
operator: "-"
example: "| - |"
coord:
  - vlg: "see Matrix Junction example"
  - hlg: "see Matrix Junction example"
```

---
### [7]
- `junction_port`, `[| |]`: a neutral connection anchor between frames.
  - Not a numeric cell token; used as a mount/bridge point.

```yaml
# Direct Example
ID: junction_port
tag: R007
operator: "[| |]"
example: "|---|----[| |]----|---|"
coord:
  - vlg: "see minimal_matrix"
  - hlg: "see minimal_matrix"
```

---
### [8]
- `matrix_bridge`, `[//]`: a matrix-level port that connects to a matrix alias.
  - Typically labeled with `ma.<alias>` to indicate the matrix target.

```yaml
# Direct Example
ID: matrix_bridge
tag: R008
operator: "[//]"
example: "|-------[//]-------|"
coord:
  - vlg: "see matrix_scaffold"
  - hlg: "see matrix_scaffold"
```

---
### [9]
- `matrix_core`, `%`: structural anchor in a frame, used to center or verify geometry.
  - No data semantics; treat as a layout marker.

```yaml
# Direct Example
ID: matrix_core
tag: R009
operator: "%"
example: "|-----|%|-----|"
coord:
  - vlg: "see Matrix Junction example"
  - hlg: "see Matrix Junction example"
```

> border
```yaml
+--+-----------------------------------------------------------------+--+
```

> sub_border
```yaml
+-----------------------------------------------------------------------+
```

> junction line gutter border
```yaml
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
```

> minimal_matrix
> - Matrix example build with nodes, subnodes, data, and junctions

```yaml
+-----------------------------------------------------------------+
|                                                                 |
|        -----------------              -----------------         |
|        |               |              |               |         |
|        -----------------              -----------------         |
|        |               |              |               |         |
|        -----------------              -----------------         |
|        -----------------              -----------------         |
|        |               |              |               |         |
|        -----------------              -----------------         |
|        |               |              |               |         |
|        -----------------              -----------------         |
|                                                                 |
|         -----------------             -----------------         |
|         |    [user]     |             |    [trixie]   |         |
|         -----------------             -----------------         |
|        ~|~(+)user   [-] |             | (+)       [-] |         |
|         | (+)       [-] |             | (+)       [-] |         |
|         | (+)       [-] |             | (+)  req  [-] |         |
|         |               |             |               |         |
|         |           |---|----[| |]----|---|           |         |
|         |           | - |     + -     | + |           |         |
|         |           |---|   matrix    |---|           |         |
|         |           | + |             | - |           |         |
|         |           |---|----[| |]----|---|           |         |
|         |               |             |               |         |
|         | (+)       [-] |             | (+)       [-] |         | 
|         | (+)       [-] |             | (+)       [-] |         |
|         | (+)       [-] |             | (+)       [-] |         |
|         | (+)       [-] |             | (+)       [-] |         |
|         -----------------             -----------------         |
|                                                                 |
|         -----------------              -----------------        |
|         |               |              |               |        |
|         -----------------              -----------------        |
|         |               |              |               |        |
|         -----------------              -----------------        |
|         -----------------              -----------------        |
|         |               |              |               |        |
|         -----------------              -----------------        |
|         |               |              |               |        |
|         -----------------              -----------------        |
|                                                                 |
+-----------------------------------------------------------------+
```

> matrix_scaffold
```yaml
+----------------------------------------------------------------+
|                                                                |
|                                                                |
|         -----------------            -----------------         |
|         |    [user]     |            |    [trixie]   |         |
|         -----------------            -----------------         |
|        ~|~(+)user[-]    |            |               |         |
|         |               |            |               |         |
|         |               |            |  (+)req[-]    |         |
|         |               |            |               |         |
|         |            |-------[//]-------|            |         |
|         |            |     ma.trixie    |            |         |
|         |            |-------[//]-------|            |         |
|         |               |            |               |         | 
|         |               |            |               |         | 
|         |               |            |               |         |
|         |               |            |               |         | 
|         |               |            |               |         | 
|         -----------------            -----------------         |
|                                                                |
|                                                                |
+----------------------------------------------------------------+
```
