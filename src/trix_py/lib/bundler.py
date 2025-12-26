"""Context Bundler — builds agent context bundles from TRIX cells.

Implements Step 4 of the Agent Protocol: Build Context.

A context bundle includes:
- Target cell with all facets
- Imported steering from other blocks
- Spatial neighbors
- Dependency status
"""

from __future__ import annotations

import json
import yaml

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class FacetContent:
    """Content of a facet."""

    path: str
    content: Optional[str] = None
    missing: bool = False


@dataclass
class CellSummary:
    """Summary of a cell for context inclusion."""

    cell_id: str
    block: str
    slot: int
    status: Optional[str] = None
    facets: Dict[str, FacetContent] = field(default_factory=dict)


@dataclass
class DepStatus:
    """Dependency status."""

    cell_id: str
    status: str
    satisfied: bool


@dataclass
class SpatialContext:
    """Spatial neighbors of a cell."""

    above: Optional[str] = None
    below: Optional[str] = None
    left: Optional[str] = None
    right: Optional[str] = None


@dataclass
class ContextBundle:
    """Complete context bundle for agent execution."""

    target: CellSummary
    imports: List[Dict[str, Any]]
    spatial: SpatialContext
    deps: List[DepStatus]
    outputs_expected: List[Dict[str, str]]
    bundled_at: str


def slot_to_rc(slot: int) -> tuple[int, int]:
    """Convert slot (1-9) to row, col (1-3, 1-3)."""
    row = ((slot - 1) // 3) + 1
    col = ((slot - 1) % 3) + 1
    return row, col


def rc_to_slot(row: int, col: int) -> Optional[int]:
    """Convert row, col to slot. Returns None if out of bounds."""
    return (row - 1) * 3 + col if 1 <= row <= 3 and 1 <= col <= 3 else None


def get_spatial_neighbors(slot: int, block: str) -> SpatialContext:
    """Get the spatial neighbors of a slot."""
    row, col = slot_to_rc(slot)

    above = rc_to_slot(row - 1, col)
    below = rc_to_slot(row + 1, col)
    left = rc_to_slot(row, col - 1)
    right = rc_to_slot(row, col + 1)

    return SpatialContext(
        above=f"{block}-{above}" if above else None,
        below=f"{block}-{below}" if below else None,
        left=f"{block}-{left}" if left else None,
        right=f"{block}-{right}" if right else None,
    )


def load_node_content(node_path: Path) -> tuple[Dict[str, Any], str]:
    """Load a node file, returning (front_matter, body)."""
    if not node_path.exists():
        return {}, ""

    text = node_path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    if not lines or lines[0].strip() != "---":
        return {}, text

    try:
        end_idx = lines[1:].index("---") + 1
        fm_text = "\n".join(lines[1:end_idx])
        body = "\n".join(lines[end_idx + 1 :])
        fm = yaml.safe_load(fm_text) or {}
        return fm, body
    except (ValueError, yaml.YAMLError):
        return {}, text


def load_map_file(map_path: Path) -> Dict[str, Any]:
    """Load a .map.yaml file."""
    if not map_path.exists():
        return {}
    try:
        return yaml.safe_load(map_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return {}


def _build_imports_context(
    trix_root: Path,
    imports_list: List[str],
    max_facet_chars: int,
) -> List[Dict[str, Any]]:
    imports: List[Dict[str, Any]] = []
    for imp_block in imports_list:
        imp_dir = trix_root / "blocks" / imp_block
        if not imp_dir.exists():
            continue

        imp_cells: List[CellSummary] = []
        for imp_slot in (5, 6):
            cell_summary = build_cell_summary(imp_block, imp_slot, imp_dir, max_facet_chars)
            if cell_summary.status:
                imp_cells.append(cell_summary)

        if imp_cells:
            imports.append(
                {
                    "block": imp_block,
                    "cells": [asdict(c) for c in imp_cells],
                }
            )
    return imports


def _build_deps_context(
    trix_root: Path,
    dep_ids: List[str],
    max_facet_chars: int,
) -> List[DepStatus]:
    deps: List[DepStatus] = []
    for dep_id in dep_ids:
        dep_parts = dep_id.split("-")
        if len(dep_parts) != 2:
            continue
        dep_block, dep_slot = dep_parts[0], int(dep_parts[1])
        dep_dir = trix_root / "blocks" / dep_block
        if not dep_dir.exists():
            continue
        dep_summary = build_cell_summary(dep_block, dep_slot, dep_dir, max_facet_chars)
        satisfied = dep_summary.status == "done"
        deps.append(
            DepStatus(
                cell_id=dep_id,
                status=dep_summary.status or "unknown",
                satisfied=satisfied,
            )
        )
    return deps


def _build_outputs_expected(links: List[Any]) -> List[Dict[str, str]]:
    return [
        {"cell_id": link["target"], "relation": link["relation"]}
        for link in links
        if isinstance(link, dict) and link.get("relation") == "produces"
    ]


def build_cell_summary(
    block: str,
    slot: int,
    block_dir: Path,
    max_facet_chars: int,
) -> CellSummary:
    """Build a summary for a single cell."""
    cell_id = f"{block}-{slot}"
    node_path = block_dir / "nodes" / f"{slot}.md"

    fm, body = load_node_content(node_path)

    facets: Dict[str, FacetContent] = {}

    # The node file itself is typically a facet
    if node_path.exists():
        node_type = fm.get("type", "doc")
        facets[node_type] = FacetContent(
            path=str(node_path),
            content=body[:max_facet_chars] if body else None,
        )

    return CellSummary(
        cell_id=cell_id,
        block=block,
        slot=slot,
        status=fm.get("status"),
        facets=facets,
    )


def build_context_bundle(
    cell_id: str,
    trix_root: Path,
    include_imports: bool = True,
    include_spatial: bool = True,
    max_facet_chars: int = 2000,
) -> ContextBundle:
    """Build a complete context bundle for a cell.

    Args:
        cell_id: Target cell (e.g., "TASK-5")
        trix_root: Root of trix_md directory
        include_imports: Whether to include imported blocks
        include_spatial: Whether to include spatial neighbors
        max_facet_chars: Maximum characters per facet content

    Returns:
        Complete ContextBundle ready for agent consumption
    """
    # Parse cell_id
    parts = cell_id.split("-")
    if len(parts) != 2:
        raise ValueError(f"Invalid cell_id format: {cell_id}")

    block = parts[0]
    slot = int(parts[1])

    # Locate block directory
    block_dir = trix_root / "blocks" / block
    if not block_dir.exists():
        raise FileNotFoundError(f"Block not found: {block}")

    # Build target cell summary
    target = build_cell_summary(block, slot, block_dir, max_facet_chars)

    # Load block map for imports
    map_path = block_dir / "matrix.md"
    matrix_fm, _ = load_node_content(map_path)
    imports_list = matrix_fm.get("imports", [])

    # Build imports context
    if include_imports:
        imports = _build_imports_context(trix_root, imports_list, max_facet_chars)
    else:
        imports = []

    # Build spatial context
    spatial = get_spatial_neighbors(slot, block) if include_spatial else SpatialContext()

    # Check dependencies
    node_path = block_dir / "nodes" / f"{slot}.md"
    node_fm, _ = load_node_content(node_path)
    dep_ids = node_fm.get("deps", [])

    deps = _build_deps_context(trix_root, dep_ids, max_facet_chars)

    # Expected outputs from links
    links = node_fm.get("links", [])
    outputs_expected = _build_outputs_expected(links)

    return ContextBundle(
        target=target,
        imports=imports,
        spatial=spatial,
        deps=deps,
        outputs_expected=outputs_expected,
        bundled_at=datetime.now(timezone.utc).isoformat(),
    )


def bundle_to_json(bundle: ContextBundle) -> str:
    """Serialize a context bundle to JSON."""
    return json.dumps(asdict(bundle), indent=2, default=str)


def bundle_to_markdown(bundle: ContextBundle) -> str:
    """Serialize a context bundle to Markdown for AI agents."""
    lines = [
        f"# Context Bundle: {bundle.target.cell_id}",
        "",
        "## Target Cell",
        f"- **Cell ID:** {bundle.target.cell_id}",
        f"- **Block:** {bundle.target.block}",
        f"- **Slot:** {bundle.target.slot}",
        f"- **Status:** {bundle.target.status or 'unknown'}",
        "",
    ]

    # Facets
    if bundle.target.facets:
        lines.append("### Facets")
        for facet_name, facet in bundle.target.facets.items():
            lines.append(f"\n#### {facet_name.title()}")
            if isinstance(facet, dict):
                content = facet.get("content", "")
            else:
                content = facet.content if hasattr(facet, "content") else ""
            if content:
                lines.extend(("```", content[:1500], "```"))
    # Imports
    if bundle.imports:
        lines.append("\n## Imported Context")
        for imp in bundle.imports:
            lines.append(f"\n### From {imp['block']}")
            lines.extend(f"- {cell['cell_id']}: {cell.get('status', 'unknown')}" for cell in imp.get("cells", []))
    # Dependencies
    if bundle.deps:
        lines.append("\n## Dependencies")
        for dep in bundle.deps:
            if isinstance(dep, DepStatus):
                dep_ok = dep.satisfied
                dep_id = dep.cell_id
                dep_status = dep.status
            else:
                dep_ok = dep.get("satisfied")
                dep_id = dep.get("cell_id")
                dep_status = dep.get("status")
            status = "✓" if dep_ok else "✗"
            lines.append(f"- {status} {dep_id} ({dep_status})")

    # Expected outputs
    if bundle.outputs_expected:
        lines.append("\n## Expected Outputs")
        lines.extend(f"- {out['cell_id']}" for out in bundle.outputs_expected)
    lines.append(f"\n---\n*Bundled at: {bundle.bundled_at}*")

    return "\n".join(lines)
