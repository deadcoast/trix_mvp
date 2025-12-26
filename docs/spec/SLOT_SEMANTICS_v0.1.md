# TRIX Slot Semantics Specification v0.1

## Overview

Every TRIX block shares the same 3×3 geometry with slots numbered 1-9, but each block **interprets** those slots for its specific domain. This document defines:

1. The **universal slot schema** (base semantics)
2. **Block-specific overrides** for each canonical block
3. **Semantic zones** that group slots by function

---

## Universal Slot Schema

```
┌─────────────────────────────────────────────────────────┐
│                    SLOT LAYOUT                         │
├─────────┬─────────┬─────────┤
│ [1]     │ [2]     │ [3]     │  ← Row 1: DEFINITION
│ Charter │ Inputs  │ Refs    │
├─────────┼─────────┼─────────┤
│ [4]     │ [5]     │ [6]     │  ← Row 2: EXECUTION
│ Backlog │ Now     │ Decide  │
├─────────┼─────────┼─────────┤
│ [7]     │ [8]     │ [9]     │  ← Row 3: COMPLETION
│ Outputs │ Valid   │ Logs    │
└─────────┴─────────┴─────────┘
```

### Semantic Zones

| Zone | Slots | Purpose |
|------|-------|---------|
| **Definition** | 1, 2, 3 | What this block is about; inputs and references |
| **Execution** | 4, 5, 6 | Active work: backlog, current focus, decisions |
| **Completion** | 7, 8, 9 | Results: outputs, validation, history |

### Column Semantics

| Column | Slots | Meaning |
|--------|-------|---------|
| **Left** | 1, 4, 7 | Primary artifacts (charter, queue, outputs) |
| **Center** | 2, 5, 8 | Flow nodes (inputs, now, validation) |
| **Right** | 3, 6, 9 | Context/metadata (refs, decisions, logs) |

---

## Block-Specific Slot Semantics

### [TASK] — Task Management

Purpose: Active work items and their lifecycle.

| Slot | Universal | TASK Override | Facets |
|------|-----------|---------------|--------|
| 1 | Charter | **Sprint Goal** — Current iteration objectives | `.task.md`, `.steer.md` |
| 2 | Inputs | **Requirements** — What tasks need to satisfy | `.doc.md` |
| 3 | References | **Blockers** — Dependencies and impediments | `.doc.md` |
| 4 | Backlog | **Backlog** — Queued tasks not yet started | `.task.md` |
| 5 | Now | **In Progress** — Currently active tasks | `.task.md`, `.steer.md` |
| 6 | Decisions | **Assignments** — Who owns what | `.doc.md` |
| 7 | Outputs | **Done** — Completed tasks (before archive) | `.task.md` |
| 8 | Validation | **Review Queue** — Tasks awaiting verification | `.task.md` |
| 9 | Logs | **Task History** — State transitions, timestamps | `.log.md` |

### [DOCS] — Documentation

Purpose: Project knowledge base and documentation artifacts.

| Slot | Universal | DOCS Override | Facets |
|------|-----------|---------------|--------|
| 1 | Charter | **Doc Strategy** — Documentation approach | `.doc.md`, `.steer.md` |
| 2 | Inputs | **Source Material** — Raw content to document | `.doc.md` |
| 3 | References | **External Refs** — Links to external docs | `.doc.md` |
| 4 | Backlog | **Doc Backlog** — Topics needing documentation | `.task.md` |
| 5 | Now | **Active Drafts** — Documents in progress | `.doc.md` |
| 6 | Decisions | **Style Guide** — Documentation conventions | `.doc.md`, `.steer.md` |
| 7 | Outputs | **Published Docs** — Finalized documentation | `.doc.md` |
| 8 | Validation | **Doc Review** — Peer review queue | `.doc.md` |
| 9 | Logs | **Change Log** — Documentation revisions | `.log.md` |

### [CODE] — Source Code

Purpose: Codebase structure and implementation artifacts.

| Slot | Universal | CODE Override | Facets |
|------|-----------|---------------|--------|
| 1 | Charter | **Code Vision** — Architecture principles | `.doc.md`, `.steer.md` |
| 2 | Inputs | **Specs** — Technical specifications | `.doc.md` |
| 3 | References | **API Index** — External API references | `.doc.md`, `.code` |
| 4 | Backlog | **Tech Debt** — Refactoring queue | `.task.md` |
| 5 | Now | **Active Branch** — Current implementation | `.code`, `.task.md` |
| 6 | Decisions | **ADRs** — Architecture Decision Records | `.doc.md` |
| 7 | Outputs | **Merged Code** — Completed implementations | `.code` |
| 8 | Validation | **PR Queue** — Code review pipeline | `.task.md` |
| 9 | Logs | **Commit Log** — Recent commits | `.log.md` |

### [ARCH] — Architecture

Purpose: System design and structural decisions.

| Slot | Universal | ARCH Override | Facets |
|------|-----------|---------------|--------|
| 1 | Charter | **System Goals** — Non-functional requirements | `.doc.md`, `.steer.md` |
| 2 | Inputs | **Constraints** — Technical limitations | `.doc.md` |
| 3 | References | **Patterns Lib** — Reference architectures | `.doc.md` |
| 4 | Backlog | **Design Proposals** — Pending designs | `.doc.md` |
| 5 | Now | **Active Design** — Current architecture work | `.doc.md`, `.steer.md` |
| 6 | Decisions | **ADR Registry** — Approved decisions | `.doc.md` |
| 7 | Outputs | **Diagrams** — Architecture artifacts | `.doc.md`, diagrams |
| 8 | Validation | **Design Review** — Architecture review queue | `.doc.md` |
| 9 | Logs | **Evolution Log** — Architecture history | `.log.md` |

### [AGNT] — Agent Configuration

Purpose: AI agent behavior and steering rules.

| Slot | Universal | AGNT Override | Facets |
|------|-----------|---------------|--------|
| 1 | Charter | **Agent Mandate** — Agent's core purpose | `.steer.md` |
| 2 | Inputs | **Context Sources** — What agent can read | `.config.yaml` |
| 3 | References | **Capabilities** — Tool/skill registry | `.doc.md` |
| 4 | Backlog | **Prompt Queue** — Pending agent tasks | `.task.md` |
| 5 | Now | **Active Session** — Current agent context | `.steer.md`, `.task.md` |
| 6 | Decisions | **Rules** — Behavioral constraints | `.steer.md` |
| 7 | Outputs | **Output Targets** — Where agent writes | `.config.yaml` |
| 8 | Validation | **Guardrails** — Safety/quality checks | `.steer.md` |
| 9 | Logs | **Session Logs** — Agent interaction history | `.log.md` |

### [TEST] — Testing

Purpose: Quality assurance and test infrastructure.

| Slot | Universal | TEST Override | Facets |
|------|-----------|---------------|--------|
| 1 | Charter | **Test Strategy** — QA approach | `.doc.md`, `.steer.md` |
| 2 | Inputs | **Test Data** — Fixtures and mocks | `.config.yaml` |
| 3 | References | **Coverage Map** — Code coverage targets | `.doc.md` |
| 4 | Backlog | **Test Backlog** — Tests to write | `.task.md` |
| 5 | Now | **Running Tests** — Active test execution | `.task.md` |
| 6 | Decisions | **Test Standards** — Testing conventions | `.steer.md` |
| 7 | Outputs | **Results** — Test reports | `.log.md`, `.metric.md` |
| 8 | Validation | **Flaky Tests** — Unstable test queue | `.task.md` |
| 9 | Logs | **CI History** — Test run history | `.log.md` |

### [DEPL] — Deployment

Purpose: Release and deployment pipeline.

| Slot | Universal | DEPL Override | Facets |
|------|-----------|---------------|--------|
| 1 | Charter | **Deploy Strategy** — Release approach | `.doc.md`, `.steer.md` |
| 2 | Inputs | **Artifacts** — Build outputs to deploy | `.config.yaml` |
| 3 | References | **Environments** — Target environments | `.config.yaml` |
| 4 | Backlog | **Release Queue** — Pending releases | `.task.md` |
| 5 | Now | **Active Deploy** — Current deployment | `.task.md` |
| 6 | Decisions | **Release Notes** — What's shipping | `.doc.md` |
| 7 | Outputs | **Deployed** — Successfully deployed versions | `.log.md` |
| 8 | Validation | **Health Checks** — Post-deploy validation | `.metric.md` |
| 9 | Logs | **Deploy Log** — Deployment history | `.log.md` |

### [OPER] — Operations

Purpose: Runtime monitoring and incident management.

| Slot | Universal | OPER Override | Facets |
|------|-----------|---------------|--------|
| 1 | Charter | **SLA/SLO** — Service level objectives | `.doc.md`, `.steer.md` |
| 2 | Inputs | **Metrics** — Incoming telemetry | `.metric.md` |
| 3 | References | **Runbooks** — Operational procedures | `.doc.md` |
| 4 | Backlog | **Alerts Backlog** — Non-urgent alerts | `.task.md` |
| 5 | Now | **Active Incidents** — Current issues | `.task.md`, `.log.md` |
| 6 | Decisions | **Escalation** — On-call decisions | `.doc.md` |
| 7 | Outputs | **Resolutions** — Incident resolutions | `.doc.md` |
| 8 | Validation | **Post-Mortems** — Incident reviews | `.doc.md` |
| 9 | Logs | **Ops Log** — Operational history | `.log.md` |

### [META] — Project Metadata

Purpose: Cross-cutting project concerns and configuration.

| Slot | Universal | META Override | Facets |
|------|-----------|---------------|--------|
| 1 | Charter | **Project Vision** — Why project exists | `.doc.md`, `.steer.md` |
| 2 | Inputs | **Dependencies** — External dependencies | `.config.yaml` |
| 3 | References | **Conventions** — Project-wide standards | `.doc.md` |
| 4 | Backlog | **Roadmap** — Long-term planning | `.doc.md` |
| 5 | Now | **Current Focus** — This iteration | `.task.md` |
| 6 | Decisions | **Project Decisions** — Key choices | `.doc.md` |
| 7 | Outputs | **Releases** — Version history | `.doc.md` |
| 8 | Validation | **Metrics** — Project health indicators | `.metric.md` |
| 9 | Logs | **Change History** — Project evolution | `.log.md` |

---

## Slot Metadata Schema

Each slot can carry metadata in its node file's YAML front matter:

```yaml
---
slot: 5
role: now            # Universal role
override: active_branch  # Block-specific override
status: active       # draft | active | blocked | done | archived
priority: 1          # 1 (highest) .. 5 (lowest)
deps:
  - TASK-2          # Dependency on another cell
  - CODE-4
tags:
  - critical
  - sprint-12
owner: "@agent/coder"
---
```

---

## Semantic Queries

The slot semantics enable powerful queries:

```
# Find all "now" slots across blocks (slot 5)
trix query --role now

# Find all outputs ready for review (slot 8)
trix query --role validation --status active

# Find TASK's in-progress items
trix query --block TASK --slot 5

# Find all charter definitions (slot 1, all blocks)
trix query --slot 1
```

---

## Implementation Notes

### Adding a New Block

1. Define the 4-char title (e.g., `[WIKI]`)
2. Create slot override table (this spec)
3. Create `blocks/<TITL>/matrix.md` with ASCII layout
4. Create `blocks/<TITL>/nodes/{1-9}.md` with front matter
5. Add to hub 9ode (HUB0)

### Semantic Inheritance

Blocks inherit the universal schema and override selectively:

- **Must preserve**: Slot numbers (1-9), row/col positions
- **Can override**: Role names, facet types, validation rules
- **Cannot change**: Spatial relationships, zone assignments

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.1 | 2024-12 | Initial specification |
