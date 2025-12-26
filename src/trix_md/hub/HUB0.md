---
kind: 9ode
title: HUB0
description: Central hub 9ode — the root navigation point for TRIX framework development.
---

# [HUB0] Central Hub

The primary 9ode organizing all 9 domain blocks for TRIX development.

```
==[HUB0]=======
[DOCS][TASK][CODE]
[ARCH][AGNT][TEST]
[DEPL][OPER][META]
===============
```

## Block Map

| Slot | Block | Purpose | Status |
|------|-------|---------|--------|
| 1 | [DOCS](../blocks/DOCS/matrix.md) | Documentation | Active |
| 2 | [TASK](../blocks/TASK/matrix.md) | Task Management | Active |
| 3 | [CODE](../blocks/CODE/matrix.md) | Source Code | Active |
| 4 | [ARCH](../blocks/ARCH/matrix.md) | Architecture | Active |
| 5 | [AGNT](../blocks/AGNT/matrix.md) | Agent Steering | Active |
| 6 | [TEST](../blocks/TEST/matrix.md) | Testing | Draft |
| 7 | [DEPL](../blocks/DEPL/matrix.md) | Deployment | Draft |
| 8 | [OPER](../blocks/OPER/matrix.md) | Operations | Draft |
| 9 | [META](../blocks/META/matrix.md) | Metadata | Active |

## Slot Semantics (9ode level)

```
┌──────────┬──────────┬──────────┐
│   DOCS   │   TASK   │   CODE   │
│   [1]    │   [2]    │   [3]    │
│Knowledge │  Work    │  Build   │
├──────────┼──────────┼──────────┤
│   ARCH   │   AGNT   │   TEST   │
│   [4]    │   [5]    │   [6]    │
│ Design   │ Steering │ Validate │
├──────────┼──────────┼──────────┤
│   DEPL   │   OPER   │   META   │
│   [7]    │   [8]    │   [9]    │
│ Release  │  Run     │  System  │
└──────────┴──────────┴──────────┘
```

## Dependency Graph

```
DOCS ◄─── ARCH ◄─── CODE
  │         │         │
  ▼         ▼         ▼
TASK ◄─── AGNT ───► TEST
  │                   │
  ▼                   ▼
DEPL ◄──────────── OPER
                      │
                      ▼
                    META
```

## Quick Navigation

### Active Work
→ [TASK-5](../blocks/TASK/nodes/5.md) — Current sprint

### Architecture
→ [ARCH-6](../blocks/ARCH/nodes/6.md) — Architecture decisions

### Agent Guidelines  
→ [AGNT-5](../blocks/AGNT/nodes/5.md) — Active steering

### Specifications
→ [DOCS-3](../blocks/DOCS/nodes/3.md) — Spec references

## Addressing Examples

From this hub:
- `TASK#5` — Slot 5 of TASK block
- `CODE#7` — Outputs slot of CODE block
- `HUB0#2#5` — TASK (slot 2) → slot 5 within TASK
