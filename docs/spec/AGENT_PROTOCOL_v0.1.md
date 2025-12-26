# TRIX Agent Protocol Specification v0.1

> **Status:** Draft  
> **Depends:** Cell Schema v0.1, Compounding v0.1, Composition v0.1  
> **Enables:** Agent implementations, dispatch systems

---

## 1. Purpose

This specification defines the **contract** for how agents interact with the TRIX steering system. It establishes the dispatch loop, context bundling, execution semantics, and write-back patterns.

The goal is to make TRIX a true **steering ecosystem** — not just storage, but an active coordinator that dispatches work to agents and records their outputs.

---

## 2. Core Principles

### 2.1 Matrix is the Source of Truth
Agents read from and write to TRIX matrices. The matrix state determines what work is available and complete.

### 2.2 Context is King
Agents receive **context bundles** — curated information relevant to their task. They don't read raw files directly.

### 2.3 Explicit Write-Back
Agents must explicitly write their outputs to designated slots. Nothing is implicitly updated.

### 2.4 Observable Execution
All agent actions are logged. The system can reconstruct what happened.

---

## 3. Agent Identity

### 3.1 Agent Schema

```yaml
agent:
  id: string              # unique identifier
  name: string            # human-readable name
  type: enum              # human | ai | script | hybrid
  capabilities: list      # what the agent can do
  constraints: list       # limitations/rules
  version: string         # agent version
```

### 3.2 Agent Types

| Type | Description | Example |
|------|-------------|---------|
| `human` | Human operator | Developer, reviewer |
| `ai` | AI model | Claude, GPT, Codex |
| `script` | Automation | CI pipeline, formatter |
| `hybrid` | AI + human review | AI drafts, human approves |

### 3.3 Capabilities

```yaml
capabilities:
  - read           # can read cells
  - write          # can write facets
  - execute        # can run transforms
  - mount          # can mount blocks
  - protect        # can protect regions
  - dispatch       # can select next task
```

### 3.4 Example Agent Definition

```yaml
agent:
  id: "codegen-v1"
  name: "Code Generator"
  type: ai
  capabilities:
    - read
    - write
    - execute
  constraints:
    - "Cannot modify protected regions"
    - "Must follow style guide at DOCS-3"
    - "Output must include tests"
  version: "1.0.0"
```

---

## 4. The Dispatch Loop

The core agent protocol is a 7-step loop:

```
┌─────────────────────────────────────────────────────────┐
│                    DISPATCH LOOP                         │
├──────────┬──────────────────────────────────────────────┤
│ Step 1   │ Read Hub                                      │
│ Step 2   │ Select Block                                  │
│ Step 3   │ Select Cell                                   │
│ Step 4   │ Build Context                                 │
│ Step 5   │ Execute Work                                  │
│ Step 6   │ Write Back                                    │
│ Step 7   │ Rollup & Log                                  │
└──────────┴──────────────────────────────────────────────┘
```

---

### 4.1 Step 1: Read Hub

**Action:** Load the hub 9ode to understand project structure.

```yaml
step: read_hub
input:
  hub_id: "HUB0"              # or project-specific hub
output:
  hub:
    titl: "HUB0"
    kind: "9ode"
    slots:
      1: { ref: "DOCS", status_summary: "80% done" }
      2: { ref: "TASK", status_summary: "3 active" }
      3: { ref: "CODE", status_summary: "blocked" }
      # ...
```

**Purpose:** Orient the agent to the available domains.

---

### 4.2 Step 2: Select Block

**Action:** Choose which block to work on based on priority and availability.

```yaml
step: select_block
input:
  hub: <from step 1>
  preference: list[titl]       # optional: preferred blocks
output:
  selected_block: "TASK"
  reason: "Has active work items with highest priority"
```

**Selection heuristics:**
1. Blocks with `status: active` cells
2. Blocks with highest priority cells
3. Blocks matching agent capabilities
4. Preference list order

---

### 4.3 Step 3: Select Cell

**Action:** Within the selected block, choose the specific cell to work on.

```yaml
step: select_cell
input:
  block: "TASK"
output:
  selected_cell: "TASK-5"
  reason: "Active, priority 2, all deps satisfied"
```

**Selection rules:**
1. Prefer slot 5 (Now) over slot 4 (Backlog)
2. Skip cells with `status: done | archived`
3. Skip cells with unmet dependencies
4. Choose highest priority among eligible cells
5. For ties, use slot order (lower first)

**Dependency check:**
```yaml
cell: TASK-5
deps: [ARCH-2, DOCS-3]

# Check each dep
ARCH-2.status: done     # ✓ satisfied
DOCS-3.status: done     # ✓ satisfied

# All deps satisfied → cell is eligible
```

---

### 4.4 Step 4: Build Context

**Action:** Assemble the context bundle for the selected cell.

```yaml
step: build_context
input:
  cell_id: "TASK-5"
  imports: ["AGNT", "ARCH", "DOCS"]  # from block imports
output:
  context_bundle: <see schema below>
```

#### Context Bundle Schema

```yaml
context_bundle:
  # ─── Target Cell ───
  target:
    cell_id: "TASK-5"
    block: "TASK"
    slot: 5
    row: 2
    col: 2
    kind: "node"
    status: "active"
    priority: 2
    facets:
      task:
        path: "nodes/TASK-5.task.md"
        content: |
          # Implement Parser
          - [ ] Extract title from header
          - [ ] Parse 3x3 cell grid
          - [ ] Validate slot numbers
      steer:
        path: "nodes/TASK-5.steer.md"
        content: |
          ## Constraints
          - Use regex for parsing
          - Handle all 4 skin types
          - Return structured AST
    deps:
      - cell_id: "ARCH-2"
        status: "done"
        satisfied: true
      - cell_id: "DOCS-3"
        status: "done"
        satisfied: true
    links:
      - target: "CODE-5"
        relation: "produces"
  
  # ─── Imported Context ───
  imports:
    - block: "AGNT"
      cells:
        - cell_id: "AGNT-5"
          facets:
            steer: |
              ## Agent Guidelines
              - Always include error handling
              - Write docstrings for public functions
              - Follow PEP 8 style guide
    - block: "ARCH"
      cells:
        - cell_id: "ARCH-2"
          facets:
            doc: |
              ## Parser Architecture
              - Skin-agnostic extraction
              - Preserve coordinates in AST
    - block: "DOCS"
      cells:
        - cell_id: "DOCS-3"
          facets:
            doc: |
              ## Parsing Specification
              - Titles: ==[TITL]===
              - Cells: [1] through [9]
  
  # ─── Spatial Context ───
  spatial:
    above: "TASK-2"          # slot directly above
    below: "TASK-8"          # slot directly below
    left: "TASK-4"           # slot to the left
    right: "TASK-6"          # slot to the right
    neighbors:
      - cell_id: "TASK-4"
        status: "done"
        summary: "Backlog complete"
      - cell_id: "TASK-6"
        status: "draft"
        summary: "Decisions pending"
  
  # ─── Output Expectations ───
  outputs:
    expected:
      - cell_id: "CODE-5"
        facet: "code"
        description: "Parser implementation"
      - cell_id: "TEST-5"
        facet: "code"
        description: "Parser tests"
    slots:
      outputs: 7    # TASK-7 for outputs
      validation: 8  # TASK-8 for test results
      logs: 9        # TASK-9 for execution log
  
  # ─── Metadata ───
  meta:
    bundled_at: "2024-01-15T10:00:00Z"
    agent_id: "codegen-v1"
    session_id: "sess_abc123"
```

---

### 4.5 Step 5: Execute Work

**Action:** Agent performs the work based on context bundle.

```yaml
step: execute
input:
  context_bundle: <from step 4>
  agent: <agent definition>
output:
  artifacts:
    - type: "code"
      path: "src/parser.py"
      content: |
        def parse_trix(path: str) -> TrixMatrix:
            ...
    - type: "code"
      path: "tests/test_parser.py"
      content: |
        def test_parse_title():
            ...
  execution_log:
    started_at: "2024-01-15T10:00:05Z"
    completed_at: "2024-01-15T10:03:42Z"
    status: "success"
    steps:
      - "Read task specification"
      - "Analyzed architecture constraints"
      - "Generated parser implementation"
      - "Generated test suite"
```

**Execution contract:**
- Agent MUST NOT modify cells outside designated outputs
- Agent MUST NOT read beyond provided context (no file system access)
- Agent MUST complete or fail explicitly (no silent hangs)

---

### 4.6 Step 6: Write Back

**Action:** Update TRIX with execution results.

```yaml
step: write_back
input:
  cell_id: "TASK-5"
  artifacts: <from step 5>
output:
  writes:
    - cell_id: "CODE-5"
      facet: "code"
      path: "nodes/CODE-5.code.py"
    - cell_id: "TEST-5"
      facet: "code"
      path: "nodes/TEST-5.test.py"
    - cell_id: "TASK-5"
      status: "done"
    - cell_id: "TASK-7"         # outputs slot
      facet: "doc"
      content: |
        ## Outputs
        - CODE-5: Parser implementation
        - TEST-5: Test suite
    - cell_id: "TASK-9"         # logs slot
      facet: "log"
      content: |
        ## Execution Log
        - Agent: codegen-v1
        - Duration: 3m 37s
        - Status: Success
```

**Write-back rules:**
1. Update target cell status to `done` (or `blocked` if failed)
2. Write artifacts to designated output cells
3. Update outputs slot (7) with summary
4. Update logs slot (9) with execution record
5. Create links between target and outputs

---

### 4.7 Step 7: Rollup & Log

**Action:** Update parent summaries and log the operation.

```yaml
step: rollup
input:
  writes: <from step 6>
output:
  rollups:
    - matrix: "TASK"
      completion: "67%"      # 6 of 9 cells done
      active_count: 2
    - matrix: "HUB0"
      slot_2:                # TASK is slot 2 of HUB0
        status_summary: "67% done"
  operation_log:
    id: "op_123"
    type: "agent_execution"
    agent_id: "codegen-v1"
    session_id: "sess_abc123"
    target: "TASK-5"
    started_at: "2024-01-15T10:00:00Z"
    completed_at: "2024-01-15T10:04:00Z"
    status: "success"
    writes:
      - "CODE-5"
      - "TEST-5"
      - "TASK-5.status"
      - "TASK-7"
      - "TASK-9"
```

---

## 5. Context Bundler

The context bundler is a service that implements Step 4.

### 5.1 Bundler Interface

```yaml
bundler:
  method: build_context
  input:
    cell_id: string
    agent_id: string
    options:
      include_spatial: bool      # include neighbor context
      include_imports: bool      # include imported blocks
      depth: int                 # how many levels of deps to include
      max_tokens: int            # limit bundle size (for AI agents)
  output:
    context_bundle: object
```

### 5.2 Bundle Formats

| Format | Use Case |
|--------|----------|
| `json` | API consumption, programmatic access |
| `yaml` | Human-readable, debugging |
| `markdown` | AI agent prompt, documentation |

**Markdown format example:**

```markdown
# Context Bundle: TASK-5

## Target Cell
- **Cell ID:** TASK-5
- **Block:** TASK
- **Slot:** 5 (row 2, col 2)
- **Status:** active
- **Priority:** 2

### Task Facet
```
# Implement Parser
- [ ] Extract title from header
- [ ] Parse 3x3 cell grid
- [ ] Validate slot numbers
```

### Steering Facet
```
## Constraints
- Use regex for parsing
- Handle all 4 skin types
```

## Imported Context

### From AGNT
[AGNT-5 steering content...]

### From ARCH
[ARCH-2 doc content...]

## Dependencies
- ✓ ARCH-2 (done)
- ✓ DOCS-3 (done)

## Expected Outputs
- CODE-5: Parser implementation
- TEST-5: Test suite
```

---

## 6. Dispatcher

The dispatcher implements Steps 1-3: selecting what to work on.

### 6.1 Dispatcher Interface

```yaml
dispatcher:
  method: select_next
  input:
    hub_id: string
    agent_id: string
    filters:
      blocks: list[titl]        # limit to these blocks
      status: list[enum]        # e.g., [active, draft]
      priority_max: int         # only priority <= this
      tags: list[string]        # must have these tags
  output:
    selected:
      cell_id: string
      reason: string
    alternatives:               # other eligible cells
      - cell_id: string
        score: float
```

### 6.2 Dispatch Strategies

| Strategy | Description |
|----------|-------------|
| `priority_first` | Highest priority eligible cell |
| `fifo` | First created eligible cell |
| `round_robin` | Rotate across blocks |
| `dependency_order` | Topological sort by deps |
| `agent_matched` | Cells matching agent capabilities |

### 6.3 Blocking Detection

A cell is **blocked** if:
- Any dependency has status ≠ `done`
- A `blocks` link exists from an incomplete cell
- It's in a protected region
- Its owner is another agent (exclusive lock)

```yaml
blocked_check:
  cell_id: "TASK-6"
  deps:
    - cell_id: "TASK-5"
      status: "active"          # NOT done
      satisfied: false
  blocking_links:
    - from: "TASK-5"
      relation: "blocks"
      status: "active"          # blocker not done
  result: blocked
  reason: "Waiting on TASK-5"
```

---

## 7. Session Management

### 7.1 Session Schema

```yaml
session:
  id: string                    # unique session ID
  agent_id: string
  started_at: datetime
  status: enum                  # active | paused | completed | failed
  current_cell: cell_id | null
  cells_processed: list[cell_id]
  context_bundle: object | null
```

### 7.2 Session Lifecycle

```
┌──────────┐     ┌──────────┐     ┌───────────┐
│  INIT    │ ──► │  ACTIVE  │ ──► │ COMPLETED │
└──────────┘     └──────────┘     └───────────┘
                      │
                      ├──► PAUSED ──► ACTIVE
                      │
                      └──► FAILED
```

### 7.3 Concurrency Rules

- Multiple sessions can read the same cell
- Only one session can write to a cell (exclusive lock)
- Lock is acquired at Step 5 (Execute), released at Step 6 (Write Back)

---

## 8. Error Handling

### 8.1 Error Types

| Error | Cause | Recovery |
|-------|-------|----------|
| `NO_ELIGIBLE_CELLS` | All cells done/blocked | Wait or reassess |
| `DEPS_UNMET` | Dependencies not satisfied | Process deps first |
| `LOCK_HELD` | Another agent owns cell | Wait or choose different cell |
| `CONTEXT_TOO_LARGE` | Bundle exceeds max_tokens | Reduce depth/imports |
| `EXECUTION_FAILED` | Agent failed during work | Log error, mark cell blocked |
| `WRITE_REJECTED` | Protected region | Choose different output |

### 8.2 Failure Handling

```yaml
on_failure:
  - mark_cell_status: "blocked"
  - set_cell_error: "<error message>"
  - log_to_slot_9: true
  - notify: ["@owner", "dispatch-monitor"]
  - release_locks: true
```

### 8.3 Retry Policy

```yaml
retry:
  max_attempts: 3
  backoff: exponential
  backoff_base: 60s
  on_final_failure: "escalate"
```

---

## 9. Observability

### 9.1 Events

All protocol steps emit events:

```yaml
event:
  type: enum                    # hub_read | block_selected | cell_selected | ...
  timestamp: datetime
  session_id: string
  agent_id: string
  data: object                  # type-specific payload
```

### 9.2 Event Types

| Event | Emitted At | Payload |
|-------|------------|---------|
| `hub_read` | Step 1 | `{ hub_id, slots_summary }` |
| `block_selected` | Step 2 | `{ block, reason }` |
| `cell_selected` | Step 3 | `{ cell_id, reason }` |
| `context_built` | Step 4 | `{ cell_id, bundle_size }` |
| `execution_started` | Step 5 | `{ cell_id }` |
| `execution_completed` | Step 5 | `{ cell_id, duration, status }` |
| `write_completed` | Step 6 | `{ writes }` |
| `rollup_completed` | Step 7 | `{ rollups }` |

### 9.3 Metrics

```yaml
metrics:
  - name: "dispatch_latency"
    description: "Time from hub_read to cell_selected"
    type: histogram
  - name: "execution_duration"
    description: "Time in Step 5"
    type: histogram
  - name: "cells_per_session"
    description: "Cells processed in one session"
    type: counter
  - name: "blocked_rate"
    description: "Fraction of cells that are blocked"
    type: gauge
```

---

## 10. Integration Patterns

### 10.1 Single Agent Loop

```python
while True:
    cell = dispatcher.select_next(hub="HUB0", agent=my_agent)
    if not cell:
        break  # no more work
    
    context = bundler.build_context(cell)
    result = agent.execute(context)
    writer.write_back(cell, result)
```

### 10.2 Multi-Agent Pool

```yaml
pool:
  agents:
    - id: "codegen-v1"
      capabilities: [read, write, execute]
      concurrency: 3
    - id: "reviewer-v1"
      capabilities: [read, write]
      concurrency: 1
  
  dispatch:
    strategy: "capability_match"
    load_balance: "round_robin"
```

### 10.3 Human-in-the-Loop

```yaml
hybrid_agent:
  id: "human-review"
  type: hybrid
  
  workflow:
    - step: "ai_draft"
      agent: "codegen-v1"
      output_status: "pending_review"
    
    - step: "human_review"
      agent: "human"
      actions: ["approve", "reject", "revise"]
    
    - step: "finalize"
      on_approve: { status: "done" }
      on_reject: { status: "blocked", reason: "review_failed" }
      on_revise: { goto: "ai_draft", context: "revision_notes" }
```

---

## 11. CLI Commands

### 11.1 Dispatch Commands

```bash
# Select next task
trix dispatch next --hub HUB0 --agent codegen-v1

# Build context for a cell
trix context TASK-5 --format markdown --output context.md

# Execute with an agent
trix execute TASK-5 --agent codegen-v1 --dry-run

# Write back results
trix write-back TASK-5 --artifacts ./output/ --status done
```

### 11.2 Query Commands

```bash
# Find eligible cells
trix query --status active --priority 1,2 --deps-met

# Check blocked cells
trix blocked --block TASK

# View session history
trix sessions --agent codegen-v1 --since "2024-01-01"
```

---

## 12. Example: Full Dispatch Cycle

```yaml
# Step 1: Read Hub
hub: HUB0
slots:
  1: DOCS (done)
  2: TASK (3 active)
  3: CODE (1 active)
  ...

# Step 2: Select Block
selected: TASK
reason: "Most active cells, highest priority"

# Step 3: Select Cell
selected: TASK-5
reason: "Priority 2, slot 5 (Now), all deps met"
alternatives:
  - TASK-4 (priority 3)
  - TASK-6 (priority 4)

# Step 4: Build Context
bundle:
  target: TASK-5
  facets: [task, steer]
  imports: [AGNT-5, ARCH-2, DOCS-3]
  spatial: [TASK-4, TASK-6, TASK-2, TASK-8]

# Step 5: Execute
agent: codegen-v1
duration: 3m 42s
artifacts:
  - CODE-5.code.py
  - TEST-5.test.py

# Step 6: Write Back
writes:
  - CODE-5.code
  - TEST-5.code
  - TASK-5.status = done
  - TASK-7 (outputs summary)
  - TASK-9 (execution log)

# Step 7: Rollup
TASK.completion: 67%
HUB0.slot_2.summary: "67% done"
operation_log: op_123
```

---

## Appendix A: Protocol Quick Reference

```
READ HUB        → Get project structure
SELECT BLOCK    → Choose domain to work in
SELECT CELL     → Choose specific task
BUILD CONTEXT   → Assemble information bundle
EXECUTE         → Agent performs work
WRITE BACK      → Update TRIX with results
ROLLUP          → Update summaries and log
```

---

## Appendix B: Changelog

| Version | Date | Changes |
|---------|------|---------|
| v0.1 | 2024-XX-XX | Initial specification |
