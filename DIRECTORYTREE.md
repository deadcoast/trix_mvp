# DIRECTORYTREE

```yaml
trix
├── AGENTS.md
├── CLAUDE.md
├── DIRECTORYTREE.md
├── Makefile
├── README.md
├── docs
│   ├── notes
│   │   └── junction_revision.md
│   └── spec
│       ├── AGENTS.md
│       ├── AGENT_PROTOCOL_v0.1.md
│       ├── CELL_SCHEMA_v0.1.md
│       ├── COMPOSITION_v0.1.md
│       ├── COMPOUNDING_v0.1.md
│       ├── SLOT_SEMANTICS_v0.1.md
│       ├── markdown
│       │   ├── ascii_design_lib.md
│       │   ├── overview.md
│       │   ├── spec-v0.1.md
│       │   └── spec-v0.2.md
│       └── schemas
│           ├── cell.schema.yaml
│           └── slot_semantics.schema.yaml
├── examples
│   ├── blocks
│   │   ├── DOCS.trix
│   │   ├── HUB0.trix
│   │   └── TASK.trix
│   ├── maps
│   │   ├── DOCS.map.yaml
│   │   ├── HUB0.map.yaml
│   │   └── TASK.map.yaml
│   └── nodes
│       ├── DOCS-1.doc.md
│       ├── DOCS-2.doc.md
│       ├── TASK-5.steer.md
│       └── TASK-5.task.md
├── main.py
├── pyproject.toml
├── src
│   ├── FutureFocus.md
│   ├── geometry_core
│   │   ├── README.md
│   │   ├── examples
│   │   │   ├── blocks
│   │   │   │   ├── CODE.trix
│   │   │   │   ├── DOCS.trix
│   │   │   │   └── TASK.trix
│   │   │   └── junctions
│   │   │       └── matrix_junction_example.md
│   │   ├── matrix_junction.md
│   │   ├── overview.md
│   │   ├── spec
│   │   │   ├── MATRIX_JUNCTION_v0_2.md
│   │   │   ├── TRIX_KERNEL_v0_3.md
│   │   │   ├── matrix_junction_ops.json
│   │   │   └── matrix_junction_ops.yaml
│   │   └── tools
│   │       ├── junction_validate.py
│   │       ├── trix.py
│   │       ├── trix_tools_patch.md
│   │       ├── trix_tools_patch.py
│   │       └── trix_tools_patch_cot.md
│   ├── trix.egg-info
│   │   ├── PKG-INFO
│   │   ├── SOURCES.txt
│   │   ├── dependency_links.txt
│   │   ├── not-zip-safe
│   │   ├── requires.txt
│   │   └── top_level.txt
│   ├── trix_md
│   │   ├── README.md
│   │   ├── blocks
│   │   │   ├── AGNT
│   │   │   │   ├── matrix.md
│   │   │   │   └── nodes
│   │   │   │       ├── 1.md
│   │   │   │       ├── 2.md
│   │   │   │       ├── 3.md
│   │   │   │       ├── 4.md
│   │   │   │       ├── 5.md
│   │   │   │       ├── 6.md
│   │   │   │       ├── 7.md
│   │   │   │       ├── 8.md
│   │   │   │       └── 9.md
│   │   │   ├── ARCH
│   │   │   │   ├── matrix.md
│   │   │   │   └── nodes
│   │   │   │       ├── 1.md
│   │   │   │       ├── 2.md
│   │   │   │       ├── 3.md
│   │   │   │       ├── 4.md
│   │   │   │       ├── 5.md
│   │   │   │       ├── 6.md
│   │   │   │       ├── 7.md
│   │   │   │       ├── 8.md
│   │   │   │       └── 9.md
│   │   │   ├── CODE
│   │   │   │   ├── matrix.md
│   │   │   │   └── nodes
│   │   │   │       ├── 1.md
│   │   │   │       ├── 2.md
│   │   │   │       ├── 3.md
│   │   │   │       ├── 4.md
│   │   │   │       ├── 5.md
│   │   │   │       ├── 6.md
│   │   │   │       ├── 7.md
│   │   │   │       ├── 8.md
│   │   │   │       └── 9.md
│   │   │   ├── DEPL
│   │   │   │   ├── matrix.md
│   │   │   │   └── nodes
│   │   │   │       ├── 1.md
│   │   │   │       ├── 2.md
│   │   │   │       ├── 3.md
│   │   │   │       ├── 4.md
│   │   │   │       ├── 5.md
│   │   │   │       ├── 6.md
│   │   │   │       ├── 7.md
│   │   │   │       ├── 8.md
│   │   │   │       └── 9.md
│   │   │   ├── DOCS
│   │   │   │   ├── matrix.md
│   │   │   │   └── nodes
│   │   │   │       ├── 1.md
│   │   │   │       ├── 2.md
│   │   │   │       ├── 3.md
│   │   │   │       ├── 4.md
│   │   │   │       ├── 5.md
│   │   │   │       ├── 6.md
│   │   │   │       ├── 7.md
│   │   │   │       ├── 8.md
│   │   │   │       └── 9.md
│   │   │   ├── META
│   │   │   │   ├── matrix.md
│   │   │   │   └── nodes
│   │   │   │       ├── 1.md
│   │   │   │       ├── 2.md
│   │   │   │       ├── 3.md
│   │   │   │       ├── 4.md
│   │   │   │       ├── 5.md
│   │   │   │       ├── 6.md
│   │   │   │       ├── 7.md
│   │   │   │       ├── 8.md
│   │   │   │       └── 9.md
│   │   │   ├── OPER
│   │   │   │   ├── matrix.md
│   │   │   │   └── nodes
│   │   │   │       ├── 1.md
│   │   │   │       ├── 2.md
│   │   │   │       ├── 3.md
│   │   │   │       ├── 4.md
│   │   │   │       ├── 5.md
│   │   │   │       ├── 6.md
│   │   │   │       ├── 7.md
│   │   │   │       ├── 8.md
│   │   │   │       └── 9.md
│   │   │   ├── TASK
│   │   │   │   ├── matrix.md
│   │   │   │   └── nodes
│   │   │   │       ├── 1.md
│   │   │   │       ├── 2.md
│   │   │   │       ├── 3.md
│   │   │   │       ├── 4.md
│   │   │   │       ├── 5.md
│   │   │   │       ├── 6.md
│   │   │   │       ├── 7.md
│   │   │   │       ├── 8.md
│   │   │   │       └── 9.md
│   │   │   └── TEST
│   │   │       ├── matrix.md
│   │   │       └── nodes
│   │   │           ├── 1.md
│   │   │           ├── 2.md
│   │   │           ├── 3.md
│   │   │           ├── 4.md
│   │   │           ├── 5.md
│   │   │           ├── 6.md
│   │   │           ├── 7.md
│   │   │           ├── 8.md
│   │   │           └── 9.md
│   │   ├── hub
│   │   │   ├── HUB0.map.yaml
│   │   │   └── HUB0.md
│   │   ├── slots.md
│   │   ├── spec
│   │   │   └── .trix.config.json
│   │   └── tools
│   │       ├── trix.code-workspace
│   │       └── trix.py
│   ├── trix_py
│   │   ├── lib
│   │   │   ├── TODO.md
│   │   │   ├── __init__.py
│   │   │   ├── bundler.py
│   │   │   ├── dispatch.py
│   │   │   ├── indexer.py
│   │   │   ├── parser.py
│   │   │   └── test_early_indexer
│   │   │       ├── __init__.py
│   │   │       └── test_early_from_json.py
│   │   └── tools
│   │       └── trix.py
│   └── trixie
│       └── trixie.md
└── uv.lock
```
