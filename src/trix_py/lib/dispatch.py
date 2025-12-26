"""Dispatcher — selects the next actionable cell from TRIX.

Implements Steps 1-3 of the Agent Protocol:
1. Read Hub
2. Select Block
3. Select Cell

The dispatcher finds eligible cells based on:
- Status (active, not done/archived)
- Dependencies (all deps must be done)
- Priority (lower number = higher priority)
"""

from __future__ import annotations

import yaml

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class CellCandidate:
    """A candidate cell for dispatch."""

    cell_id: str
    block: str
    slot: int
    status: str
    priority: Optional[int]
    deps: List[str]
    deps_satisfied: bool
    score: float  # Lower is better


@dataclass
class DispatchResult:
    """Result of dispatch selection."""

    selected: Optional[CellCandidate]
    reason: str
    alternatives: List[CellCandidate]


def load_front_matter(path: Path) -> Dict[str, Any]:
    """Load YAML front matter from a markdown file."""
    if not path.exists():
        return {}

    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    if not lines or lines[0].strip() != "---":
        return {}

    try:
        end_idx = lines[1:].index("---") + 1
        fm_text = "\n".join(lines[1:end_idx])
        return yaml.safe_load(fm_text) or {}
    except (ValueError, yaml.YAMLError):
        return {}


def get_cell_status(block: str, slot: int, trix_root: Path) -> Tuple[str, Optional[int], List[str]]:
    """Get status, priority, and deps for a cell."""
    node_path = trix_root / "blocks" / block / "nodes" / f"{slot}.md"
    fm = load_front_matter(node_path)

    status = fm.get("status", "unknown")
    priority = fm.get("priority")
    deps = fm.get("deps", [])

    return status, priority, deps


def check_deps_satisfied(deps: List[str], trix_root: Path) -> bool:
    """Check if all dependencies are satisfied (status = done)."""
    if not deps:
        return True

    for dep_id in deps:
        parts = dep_id.split("-")
        if len(parts) != 2:
            continue

        dep_block, dep_slot = parts[0], int(parts[1])
        status, _, _ = get_cell_status(dep_block, dep_slot, trix_root)

        if status != "done":
            return False

    return True


def calculate_score(
    slot: int,
    priority: Optional[int],
    status: str,
) -> float:
    """Calculate dispatch score (lower is better).

    Scoring factors:
    - Priority: 1-5 (1 is highest priority)
    - Slot preference: slot 5 (Now) preferred over slot 4 (Backlog)
    - Status: active preferred over draft
    """
    score = 0.0

    # Priority contribution (0-50 points)
    if priority:
        score += priority * 10
    else:
        score += 30  # Default to medium priority

    # Slot preference (0-10 points)
    if slot == 5:  # Now slot
        score += 0
    elif slot == 4:  # Backlog slot
        score += 5
    else:
        score += 10

    # Status preference
    if status == "active":
        score += 0
    elif status == "draft":
        score += 20
    else:
        score += 100  # blocked, done, archived

    return score


def scan_block(block: str, trix_root: Path) -> List[CellCandidate]:
    """Scan a block for candidate cells."""
    candidates: List[CellCandidate] = []

    block_dir = trix_root / "blocks" / block
    if not block_dir.exists():
        return candidates

    # Check slots 4 (Backlog) and 5 (Now) primarily
    for slot in [5, 4, 1, 2, 3, 6, 7, 8, 9]:
        status, priority, deps = get_cell_status(block, slot, trix_root)

        # Skip completed or archived cells
        if status in ("done", "archived"):
            continue

        deps_satisfied = check_deps_satisfied(deps, trix_root)

        # Skip blocked cells (status=blocked OR deps not satisfied)
        if status == "blocked" or (deps and not deps_satisfied):
            continue

        score = calculate_score(slot, priority, status)

        candidates.append(
            CellCandidate(
                cell_id=f"{block}-{slot}",
                block=block,
                slot=slot,
                status=status,
                priority=priority,
                deps=deps,
                deps_satisfied=deps_satisfied,
                score=score,
            )
        )

    return candidates


def read_hub(hub_path: Path) -> List[str]:
    """Read the hub and return list of block references."""
    fm = load_front_matter(hub_path)

    # For 9ode, we need to extract block refs
    # For now, we'll use a known list based on our structure
    blocks = ["DOCS", "TASK", "CODE", "ARCH", "AGNT", "TEST", "DEPL", "OPER", "META"]

    return blocks


def select_next(
    trix_root: Path,
    hub_path: Optional[Path] = None,
    block_filter: Optional[List[str]] = None,
    priority_max: Optional[int] = None,
) -> DispatchResult:
    """Select the next actionable cell.

    Args:
        trix_root: Root of trix_md directory
        hub_path: Path to hub file (defaults to hub/HUB0.md)
        block_filter: Only consider these blocks
        priority_max: Only consider priority <= this value

    Returns:
        DispatchResult with selected cell and alternatives
    """
    if hub_path is None:
        hub_path = trix_root / "hub" / "HUB0.md"

    # Step 1: Read Hub
    blocks = read_hub(hub_path)

    if block_filter:
        blocks = [b for b in blocks if b in block_filter]

    # Step 2 & 3: Scan blocks and select cells
    all_candidates: List[CellCandidate] = []

    for block in blocks:
        candidates = scan_block(block, trix_root)
        all_candidates.extend(candidates)

    # Filter by priority
    if priority_max is not None:
        all_candidates = [c for c in all_candidates if c.priority is None or c.priority <= priority_max]

    if not all_candidates:
        return DispatchResult(
            selected=None,
            reason="No eligible cells found",
            alternatives=[],
        )

    # Sort by score (lower is better)
    all_candidates.sort(key=lambda c: c.score)

    selected = all_candidates[0]
    alternatives = all_candidates[1:5]  # Top 5 alternatives

    reason_parts = []
    if selected.slot == 5:
        reason_parts.append("Now slot")
    if selected.priority and selected.priority <= 2:
        reason_parts.append(f"priority {selected.priority}")
    if selected.status == "active":
        reason_parts.append("active status")
    if selected.deps_satisfied:
        reason_parts.append("deps satisfied")

    reason = ", ".join(reason_parts) if reason_parts else "best available"

    return DispatchResult(
        selected=selected,
        reason=reason,
        alternatives=alternatives,
    )


def dispatch_to_json(result: DispatchResult) -> str:
    """Serialize dispatch result to JSON."""
    import json

    from dataclasses import asdict

    data = {
        "selected": asdict(result.selected) if result.selected else None,
        "reason": result.reason,
        "alternatives": [asdict(a) for a in result.alternatives],
    }

    return json.dumps(data, indent=2)
