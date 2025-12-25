### `matrix_junction` design

```toml
[agent]
agent.trix = "trixie"

[trixie]
trixie.agents = "trixie"
trixie.req = "requirements"
trixie.steer = "steering

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
ID: R001 
  rule: "As soon as a export node is detected, its parent alias is saved as a `key` in the user input data map."
    example: "'(+)user' -> '(+u)'"
  rule: formatting
    form: 
R002:
R003:

```

> sub_border
```yaml
----------------- 
|               |
----------------- 
```

## Matrix Junctions

> Matrix 1:1 Node Grid 3x3
- The following example is designed so you can see all asoects in how the junctions integrate into the matrix

- Line Border Gutters: "Example below will use `vlg`, `hlg` for coordinates in explabnations"
  - `matrix_junction`, `trix_junct`: The matrix housing blocks
  - `vertical_line_gutter`, `vlg`
  - `horizontal_line_gutter`, `hlg`
  - `coordinates`, `coord`: coordinates to reference specific assets in the `trix_junct`
  - `operator`: if applicaple, a character the asset uses to represent itself in the matrix
  - `tag`: a `RuleID` for the asset `R` plus three numbers `000` = `R000`
  - `description`
  - `example`, `eg`,

> Matrix Junction
```yaml
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
- `eg`: real example of the asset from the 
  - `coord`,
    - `vlg`,
    - `hlg`
```

```yaml
ID:
tag:
example:
  coord:
    - vlg:
    - hlg: 
```

---
### [1]
- `coupler`, `-|-`: acts as a "coupler" in the matrix, locking nodes into place, Only required to protect important nodes from being overriten or changed.

```yaml
# Direct Example
ID: coupler
tag: R002
  example: '|-|-|'
  coord:
    - vlg: 06->07
    - hlg: 09->10
```

---
### [2]
- `patch`, `~`: allows nodes to connect data workflows between nodes in the junctions

```yaml
# Direct Example
ID: patch
tag: R003
example: '~|~'
  coord:
    - vlg: 13
    - hlg: 21->23
```

- [1]
  - vlg:
  - hlg:

- [2]
  - vlg:
  - hlg:
- [3]
  - vlg:
  - hlg:
- [4]
  - vlg:
  - hlg:

- [5]
  - vlg:
  - hlg:

- [6]
  - vlg:
  - hlg:

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
