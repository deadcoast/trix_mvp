#!/usr/bin/env python3
"""trix CLI (MVP)

Commands:
  - validate : validate matrix structure + links
  - index    : build trix/.index/trix_index.json
  - next     : print next task candidate from TASK block

This is intentionally small: extend to your taste.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import yaml

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


FRONT_MATTER_DELIM = "---"


@dataclass(frozen=True)
class MatrixCell:
    label: str
    target: str


def die(msg: str, code: int = 1) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(code)


def load_json(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        die(f"Missing config: {path}")
    except json.JSONDecodeError as e:
        die(f"Invalid JSON in {path}: {e}")


def split_front_matter(text: str) -> Tuple[Dict[str, Any], str]:
    """Return (front_matter_dict, body_text)."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != FRONT_MATTER_DELIM:
        return {}, text

    # find second delimiter
    try:
        end = lines[1:].index(FRONT_MATTER_DELIM) + 1
    except ValueError:
        die("Front matter starts with '---' but never ends with '---'")
    fm_text = "\n".join(lines[1:end])
    body = "\n".join(lines[end + 1 :])
    try:
        fm = yaml.safe_load(fm_text) or {}
        if not isinstance(fm, dict):
            die("Front matter must be a YAML mapping (key: value)")
        return fm, body
    except yaml.YAMLError as e:
        die(f"Invalid YAML front matter: {e}")


def read_front_matter(path: Path) -> Dict[str, Any]:
    fm, _ = split_front_matter(path.read_text(encoding="utf-8"))
    return fm


def extract_matrix_row_lines(body: str) -> List[str]:
    """Extract the 3 matrix rows.

    MVP rule: any line that starts with '|' is treated as a matrix row.
    """
    return [line.strip() for line in body.splitlines() if line.strip().startswith("|")]


def parse_block_row(row: str) -> List[MatrixCell]:
    # Matches [1](path) ... for 3 cells in a row
    pattern = re.compile(r"\[(\d)\]\(([^)]+)\)")
    return [MatrixCell(label=m.group(1), target=m.group(2)) for m in pattern.finditer(row)]


def parse_9ode_row(row: str) -> List[MatrixCell]:
    # Matches [DOCS](path) ... for 3 cells in a row
    pattern = re.compile(r"\[([A-Za-z0-9]{4})\]\(([^)]+)\)")
    return [MatrixCell(label=m.group(1), target=m.group(2)) for m in pattern.finditer(row)]


def resolve_target(matrix_path: Path, target: str) -> Path:
    # Allow absolute or relative paths; MVP treats as file paths.
    p = Path(target)
    return p if p.is_absolute() else (matrix_path.parent / p).resolve()


def validate_matrix_file(path: Path) -> List[str]:
    """Validate a single matrix file and return warnings (non-fatal)."""
    warnings: List[str] = []
    text = path.read_text(encoding="utf-8")
    fm, body = split_front_matter(text)

    kind = (fm.get("kind") or "").strip()
    title = (fm.get("title") or "").strip()

    if not kind:
        die(f"{path}: missing front matter 'kind'")
    if kind not in {"block", "9ode", "super"}:
        die(f"{path}: unknown kind '{kind}' (expected block|9ode|super)")
    if not title:
        die(f"{path}: missing front matter 'title'")
    if len(title) != 4:
        die(f"{path}: title '{title}' must be 4 characters")

    # basic '==[TITL]' presence (not strict)
    if f"==[{title}]" not in text:
        warnings.append(f"{path}: matrix header does not include '==[{title}]' (not fatal)")

    rows = extract_matrix_row_lines(body)
    if len(rows) != 3:
        die(f"{path}: expected 3 matrix rows starting with '|', found {len(rows)}")

    for i, row in enumerate(rows, start=1):
        cells = parse_block_row(row) if kind == "block" else parse_9ode_row(row)
        if len(cells) != 3:
            die(f"{path}: row {i} expected 3 cells, found {len(cells)}. Row: {row}")

        for cell in cells:
            target_path = resolve_target(path, cell.target)
            if not target_path.exists():
                die(f"{path}: missing target for cell [{cell.label}] -> {cell.target} (resolved {target_path})")

    # block-specific checks
    if kind == "block":
        # Ensure we have slots 1..9 exactly once in matrix links
        all_cells = []
        for row in rows:
            all_cells.extend(parse_block_row(row))
        labels = [c.label for c in all_cells]
        if sorted(labels) != [str(i) for i in range(1, 10)]:
            warnings.append(f"{path}: expected slots 1..9 once each, saw {labels}")

    return warnings


def find_matrix_files(root: Path) -> List[Path]:
    # any file named matrix.md plus hub file(s)
    files: List[Path] = []
    files.extend(root.glob("trix/hub/*.md"))
    files.extend(root.glob("trix/blocks/*/matrix.md"))
    return sorted(set(files))


def build_index(root: Path) -> Dict[str, Any]:
    idx: Dict[str, Any] = {
        "blocks": {},
        "nodes": {},
    }

    matrix_files = find_matrix_files(root)
    for mpath in matrix_files:
        fm = read_front_matter(mpath)
        kind = fm.get("kind")
        title = fm.get("title")

        # Parse cells to attach link graph
        _, body = split_front_matter(mpath.read_text(encoding="utf-8"))
        rows = extract_matrix_row_lines(body)

        cells: List[MatrixCell] = []
        if kind == "block":
            for r in rows:
                cells.extend(parse_block_row(r))
            idx["blocks"][title] = {
                "kind": "block",
                "path": str(mpath.relative_to(root)),
                "cells": [{"slot": c.label, "target": c.target} for c in cells],
            }
            # Load node front matter
            for c in cells:
                node_path = resolve_target(mpath, c.target)
                nfm, _ = split_front_matter(node_path.read_text(encoding="utf-8"))
                node_id = nfm.get("node_id") or f"{title}-{c.label}"
                idx["nodes"][node_id] = {
                    "path": str(node_path.relative_to(root)),
                    "block": nfm.get("block") or title,
                    "slot": int(nfm.get("slot") or c.label),
                    "type": nfm.get("type") or "doc",
                    "status": nfm.get("status") or "unknown",
                    "tags": nfm.get("tags") or [],
                    "links": nfm.get("links") or [],
                }
        else:
            for r in rows:
                cells.extend(parse_9ode_row(r))
            idx["blocks"][title] = {
                "kind": kind,
                "path": str(mpath.relative_to(root)),
                "cells": [{"label": c.label, "target": c.target} for c in cells],
            }

    return idx


def cmd_validate(args: argparse.Namespace) -> None:
    repo = Path(args.repo).resolve()
    files = find_matrix_files(repo)
    if not files:
        die(f"No matrix files found under {repo}/trix")
    warnings_total: List[str] = []
    for f in files:
        warnings_total.extend(validate_matrix_file(f))

    print(f"OK: validated {len(files)} matrix files")
    if warnings_total:
        print("\nWarnings:")
        for w in warnings_total:
            print(f"- {w}")


def cmd_index(args: argparse.Namespace) -> None:
    repo = Path(args.repo).resolve()
    idx = build_index(repo)
    out = repo / "trix" / ".index" / "trix_index.json"
    out.write_text(json.dumps(idx, indent=2), encoding="utf-8")
    print(f"Wrote {out} ({len(idx['blocks'])} matrices, {len(idx['nodes'])} nodes)")


def find_next_task_markdown(path: Path) -> Optional[str]:
    text = path.read_text(encoding="utf-8")
    return next((line.strip() for line in text.splitlines() if "- [ ]" in line), None)


def cmd_next(args: argparse.Namespace) -> None:
    repo = Path(args.repo).resolve()
    idx_path = repo / "trix" / ".index" / "trix_index.json"
    if idx_path.exists():
        idx = json.loads(idx_path.read_text(encoding="utf-8"))
    else:
        idx = build_index(repo)

    task_block = "TASK"
    candidates = [
        (n.get("slot"), nid, n)
        for nid, n in idx.get("nodes", {}).items()
        if n.get("block") == task_block and n.get("type") == "task"
    ]
    candidates.sort(key=lambda t: (t[0], t[1]))
    for slot, nid, n in candidates:
        if slot not in (4, 5):
            continue
        if task_line := find_next_task_markdown(repo / n["path"]):
            print(f"Next task candidate ({nid}): {task_line}")
            return

    print("No open tasks found in TASK slots 4 or 5.")
    return


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--repo",
        default=str(Path(__file__).resolve().parents[1]),
        help="repo root (default: script/..)",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("validate")
    sub.add_parser("index")
    sub.add_parser("next")

    args = p.parse_args()

    if args.cmd == "validate":
        cmd_validate(args)
    elif args.cmd == "index":
        cmd_index(args)
    elif args.cmd == "next":
        cmd_next(args)
    else:
        die(f"Unknown cmd: {args.cmd}")


if __name__ == "__main__":
    main()
