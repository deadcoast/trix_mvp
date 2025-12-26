#!/usr/bin/env python3
"""
TRIX geometry-first helper tools (v0.4)

This toolset is intentionally lightweight and repo-agnostic.

Core goals:
- Preserve matrix geometry (cells + coordinates).
- Support *pinpoint referencing* via gutters:
  - Overlay gutters (L#### / C####) for any text file.
  - Native junction gutters (vlg/hlg) as defined in matrix_junction.md.
- Parse common ASCII skins by extracting:
  - TITL ([ABCD])
  - the 3×3 numeric slots [1]..[9] and their visual positions.
- Scan "junction" canvases for multiple embedded matrices and resolve a coordinate to:
  - matrix title + slot (TRIX address).

Notes:
- This does NOT try to be a full TRIX runtime engine.
- It is a geometry kernel that other layers (bindings, facets, transforms, trixie) can build on.
"""

from __future__ import annotations

import argparse
import json
import sys

from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol

try:
    from . import junction_validate
    from .trix_bindings import _parse_facet_filter, _resolve_pin_location, resolve_pin_to_binding
    from .trix_blocks import (
        parse_first_block,
        rc_to_slot,
        resolve_coordinate,
        scan_junction,
        slot_to_rc,
    )
    from .trix_gutters import (
        _guttered_vlg_hlg_to_lc,
        _parse_lc,
        extract_region_vlg_hlg,
        gutter_overlay,
        normalize_lines,
        read_text,
    )
    from .trix_validate import _extract_labeled_blocks
except ImportError:  # pragma: no cover
    tool_root = Path(__file__).resolve().parent
    if str(tool_root) not in sys.path:
        sys.path.insert(0, str(tool_root))
    import junction_validate
    from trix_bindings import _parse_facet_filter, _resolve_pin_location, resolve_pin_to_binding
    from trix_blocks import parse_first_block, rc_to_slot, resolve_coordinate, scan_junction, slot_to_rc
    from trix_gutters import (
        _guttered_vlg_hlg_to_lc,
        _parse_lc,
        extract_region_vlg_hlg,
        gutter_overlay,
        normalize_lines,
        read_text,
    )
    from trix_validate import _extract_labeled_blocks


class _PathArgs(Protocol):
    """Args that carry a path."""

    path: str


class _AddrArgs(Protocol):
    """Args for slot/row/col conversions."""

    slot: Optional[int]
    row: Optional[int]
    col: Optional[int]


class _ResolveArgs(_PathArgs, Protocol):
    """Args for coordinate resolution."""

    lc: Optional[str]
    line: Optional[int]
    col: Optional[int]
    vlg: Optional[int]
    hlg: Optional[int]


class _PinArgs(_ResolveArgs, Protocol):
    """Args for pin resolution with facets."""

    repo: str
    facet: Optional[List[str]]
    max_chars: int


class _ContentArgs(_ResolveArgs, Protocol):
    """Args for full content resolution."""

    repo: str
    facet: Optional[List[str]]


class _ValidateArgs(_PathArgs, Protocol):
    """Args for operator validation."""

    spec: Optional[str]


class _ExtractArgs(_PathArgs, Protocol):
    """Args for vlg/hlg extraction."""

    vlg0: int
    vlg1: int
    hlg0: int
    hlg1: int


class _IndexArgs(Protocol):
    """Args for repo indexing."""

    root: str
    out: str


def cmd_gutter(args: _PathArgs) -> int:
    """Print a file with overlay L/C gutters."""
    path = Path(args.path)
    print(gutter_overlay(read_text(path)))
    return 0


def cmd_addr(args: _AddrArgs) -> int:
    """Convert between slot and row/col coordinates."""
    if args.slot is not None:
        r, c = slot_to_rc(args.slot)
        print(json.dumps({"slot": args.slot, "row": r, "col": c}, indent=2))
        return 0
    if args.row is not None and args.col is not None:
        slot = rc_to_slot(args.row, args.col)
        print(json.dumps({"row": args.row, "col": args.col, "slot": slot}, indent=2))
        return 0
    raise SystemExit("addr requires either --slot or --row and --col")


def cmd_parse(args: _PathArgs) -> int:
    """Parse the first 3x3 block in a file."""
    path = Path(args.path)
    block = parse_first_block(read_text(path))
    print(json.dumps(asdict(block), indent=2))
    return 0


def cmd_scan(args: _PathArgs) -> int:
    """Scan a junction canvas for embedded 3x3 blocks."""
    path = Path(args.path)
    embedded = scan_junction(read_text(path))
    print(
        json.dumps(
            [
                {
                    "titl": e.titl,
                    "anchor_line": e.anchor_line,
                    "anchor_col": e.anchor_col,
                    "bbox": e.bbox,
                    "rows": e.block.rows,
                    "row_lines": e.block.row_lines,
                    "skin": e.block.skin,
                    "cells": [asdict(c) for c in e.block.cells],
                }
                for e in embedded
            ],
            indent=2,
        )
    )
    return 0


def cmd_resolve(args: _ResolveArgs) -> int:
    """Resolve a coordinate to a TRIX address."""
    path = Path(args.path)
    text = read_text(path)
    lines = normalize_lines(text)

    if args.lc:
        line, col = _parse_lc(args.lc)
    elif args.line is not None and args.col is not None:
        line, col = args.line, args.col
    elif args.vlg is not None and args.hlg is not None:
        line, col = _guttered_vlg_hlg_to_lc(lines, args.vlg, args.hlg)
    else:
        raise SystemExit("resolve requires either --lc, --line/--col, or --vlg/--hlg")

    result = resolve_coordinate(text, line=line, col=col)
    print(json.dumps(result, indent=2))
    return 0


def cmd_pin(args: _PinArgs) -> int:
    """Resolve a coordinate to a binding with facet excerpts."""
    path = Path(args.path)
    text = read_text(path)
    lines = normalize_lines(text)
    repo_root = Path(args.repo).resolve()

    line, col, pin_meta = _resolve_pin_location(
        lines=lines,
        lc=args.lc,
        line=args.line,
        col=args.col,
        vlg=args.vlg,
        hlg=args.hlg,
    )

    resolved = resolve_coordinate(text, line=line, col=col)
    hit = resolved.get("hit") if isinstance(resolved, dict) else None
    binding = None
    if isinstance(hit, dict):
        matrix = hit.get("matrix")
        slot = hit.get("slot")
        token = hit.get("token")
    else:
        matrix = None
        slot = None
        token = None

    if isinstance(matrix, str) and isinstance(slot, int):
        binding = resolve_pin_to_binding(
            repo_root,
            titl=matrix,
            slot=slot,
            token=token if isinstance(token, int) else None,
            full=False,
            max_chars=args.max_chars,
            facet_filter=_parse_facet_filter(args.facet),
        )

    payload = {"pin": pin_meta, "resolved": resolved, "binding": binding}
    print(json.dumps(payload, indent=2))
    return 0


def cmd_content(args: _ContentArgs) -> int:
    """Resolve a coordinate to a binding with full facet content."""
    path = Path(args.path)
    text = read_text(path)
    lines = normalize_lines(text)
    repo_root = Path(args.repo).resolve()

    line, col, pin_meta = _resolve_pin_location(
        lines=lines,
        lc=args.lc,
        line=args.line,
        col=args.col,
        vlg=args.vlg,
        hlg=args.hlg,
    )

    resolved = resolve_coordinate(text, line=line, col=col)
    hit = resolved.get("hit") if isinstance(resolved, dict) else None
    binding = None
    if isinstance(hit, dict):
        matrix = hit.get("matrix")
        slot = hit.get("slot")
        token = hit.get("token")
    else:
        matrix = None
        slot = None
        token = None

    if isinstance(matrix, str) and isinstance(slot, int):
        binding = resolve_pin_to_binding(
            repo_root,
            titl=matrix,
            slot=slot,
            token=token if isinstance(token, int) else None,
            full=True,
            max_chars=0,
            facet_filter=_parse_facet_filter(args.facet),
        )

    payload = {"pin": pin_meta, "resolved": resolved, "binding": binding}
    print(json.dumps(payload, indent=2))
    return 0


def cmd_validate(args: _ValidateArgs) -> int:
    """Validate operator placement using a spec or inline summary table."""
    path = Path(args.path)
    text = read_text(path)
    labeled_blocks = _extract_labeled_blocks(text)

    skipped: List[str] = []
    if args.spec:
        expected = junction_validate.load_expectations(Path(args.spec))
    else:
        expected, skipped = junction_validate.parse_operator_summary(text)

    if not expected:
        raise SystemExit("validate requires --spec or an Operator Summary table in the file")

    default_block = "minimal_matrix" if "minimal_matrix" in labeled_blocks else None
    grouped: Dict[Optional[str], List[junction_validate.OperatorExpectation]] = {}
    for entry in expected:
        block = entry.block or default_block
        grouped.setdefault(block, []).append(entry)

    errors: List[Dict[str, Any]] = []
    checked = 0
    for block, entries in grouped.items():
        if block is None:
            block_text = text
        else:
            block_text = labeled_blocks.get(block)
            if block_text is None:
                for entry in entries:
                    errors.append(
                        {
                            "operator": entry.operator,
                            "rule": entry.rule,
                            "block": block,
                            "vlg": [entry.vlg0, entry.vlg1],
                            "hlg": [entry.hlg0, entry.hlg1],
                            "region": "",
                            "error": "block not found",
                        }
                    )
                checked += len(entries)
                continue

        result = junction_validate.validate_expectations(
            block_text,
            entries,
            extract_region_vlg_hlg,
        )
        checked += int(result.get("checked", 0))
        for err in result.get("errors", []):
            if block is not None:
                err["block"] = block
        errors.extend(result.get("errors", []))

    payload = {"path": str(path), "checked": checked, "errors": errors}
    if skipped:
        payload["skipped"] = skipped
    print(json.dumps(payload, indent=2))
    return 2 if errors else 0


def cmd_extract(args: _ExtractArgs) -> int:
    """Extract a vlg/hlg rectangular region from a junction canvas."""
    path = Path(args.path)
    text = read_text(path)
    result = extract_region_vlg_hlg(text, args.vlg0, args.vlg1, args.hlg0, args.hlg1)
    print(json.dumps(result, indent=2))
    return 0


def cmd_index(args: _IndexArgs) -> int:
    """Scan a repo tree for embedded 3x3 blocks and write an index."""
    root = Path(args.root)
    out_path = Path(args.out)
    records = []
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix.lower() not in {".md", ".txt", ".trix"}:
            continue
        try:
            text = read_text(p)
        except OSError:
            continue
        if "[" not in text or "]" not in text:
            continue
        try:
            blocks = scan_junction(text)
        except ValueError:
            continue
        if not blocks:
            continue
        records.append(
            {
                "path": str(p.relative_to(root)),
                "embedded": [
                    {
                        "titl": b.titl,
                        "anchor_line": b.anchor_line,
                        "anchor_col": b.anchor_col,
                        "bbox": b.bbox,
                        "rows": b.block.rows,
                        "row_lines": b.block.row_lines,
                        "skin": b.block.skin,
                        "cells": [asdict(c) for c in b.block.cells],
                    }
                    for b in blocks
                ],
            }
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps({"root": str(root), "records": records}, indent=2),
        encoding="utf-8",
    )
    print(f"Wrote index: {out_path} ({len(records)} files)")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    p = argparse.ArgumentParser(prog="trix", description="TRIX geometry-first helper tools")
    sub = p.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("gutter", help="print a file with L/C gutters for pinpoint references")
    g.add_argument("path")
    g.set_defaults(func=cmd_gutter)

    a = sub.add_parser("addr", help="convert between slot and row/col for a 3×3 block")
    a.add_argument("--slot", type=int)
    a.add_argument("--row", type=int)
    a.add_argument("--col", type=int)
    a.set_defaults(func=cmd_addr)

    pr = sub.add_parser("parse", help="parse the first 3×3 block in a file")
    pr.add_argument("path")
    pr.set_defaults(func=cmd_parse)

    sc = sub.add_parser("scan", help="scan a file (junction canvas) for embedded 3×3 blocks")
    sc.add_argument("path")
    sc.set_defaults(func=cmd_scan)

    rs = sub.add_parser("resolve", help="resolve a coordinate to matrix+slot (TRIX address)")
    rs.add_argument("path")
    rs.add_argument("--lc", help="Coordinate like L0042:C0137")
    rs.add_argument("--line", type=int, help="0-based line index")
    rs.add_argument("--col", type=int, help="0-based column index")
    rs.add_argument(
        "--vlg",
        type=int,
        help="Vertical line gutter index (native junction style, 2-digit rows)",
    )
    rs.add_argument("--hlg", type=int, help="Horizontal line gutter index (native junction style)")
    rs.set_defaults(func=cmd_resolve)

    pn = sub.add_parser("pin", help="resolve a coordinate to binding + facet excerpts")
    pn.add_argument("path")
    pn.add_argument("--repo", default=".", help="Repo root for resolving .map.yaml and facets")
    pn.add_argument("--lc", help="Coordinate like L0042:C0137")
    pn.add_argument("--line", type=int, help="0-based line index")
    pn.add_argument("--col", type=int, help="0-based column index")
    pn.add_argument("--vlg", type=int, help="Vertical line gutter index (native junction style)")
    pn.add_argument("--hlg", type=int, help="Horizontal line gutter index (native junction style)")
    pn.add_argument("--facet", action="append", help="Facet filter (repeatable or comma-separated)")
    pn.add_argument("--max-chars", type=int, default=1400, help="Excerpt length for facets")
    pn.set_defaults(func=cmd_pin)

    ct = sub.add_parser("content", help="resolve a coordinate to full facet contents")
    ct.add_argument("path")
    ct.add_argument("--repo", default=".", help="Repo root for resolving .map.yaml and facets")
    ct.add_argument("--lc", help="Coordinate like L0042:C0137")
    ct.add_argument("--line", type=int, help="0-based line index")
    ct.add_argument("--col", type=int, help="0-based column index")
    ct.add_argument("--vlg", type=int, help="Vertical line gutter index (native junction style)")
    ct.add_argument("--hlg", type=int, help="Horizontal line gutter index (native junction style)")
    ct.add_argument("--facet", action="append", help="Facet filter (repeatable or comma-separated)")
    ct.set_defaults(func=cmd_content)

    vd = sub.add_parser("validate", help="validate operator coords against a guttered junction")
    vd.add_argument("path")
    vd.add_argument("--spec", help="YAML/JSON with operator coords (optional)")
    vd.set_defaults(func=cmd_validate)

    ex = sub.add_parser(
        "extract",
        help="extract a (vlg/hlg) rectangular region from a native-gutter junction",
    )
    ex.add_argument("path")
    ex.add_argument("--vlg0", type=int, required=True)
    ex.add_argument("--vlg1", type=int, required=True)
    ex.add_argument("--hlg0", type=int, required=True)
    ex.add_argument("--hlg1", type=int, required=True)
    ex.set_defaults(func=cmd_extract)

    ix = sub.add_parser("index", help="scan a repo tree for embedded blocks and write a JSON index")
    ix.add_argument("root")
    ix.add_argument("--out", default=".trix/index.json")
    ix.set_defaults(func=cmd_index)

    return p


def main() -> int:
    """Entry point for the trix CLI."""
    p = build_parser()
    args = p.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
