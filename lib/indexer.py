from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, Optional, List
import json

import yaml

from .parser import parse_trix, validate_block_3x3


@dataclass
class CellBinding:
    kind: str                # node | block | 9ode | super | link | empty
    token: str               # raw token in [..]
    slot: int                # 1..9 for block
    row: int
    col: int
    payload: Dict[str, Any]  # mapping content


@dataclass
class MatrixRecord:
    titl: str
    path: str
    skin_hint: Optional[str]
    cells: List[CellBinding]


def load_map_for_matrix(matrix_path: Path) -> Optional[Dict[str, Any]]:
    """Look for a mapping file for a given matrix.

    Common patterns:
      - same folder: TASK.trix -> TASK.map.yaml
      - sibling 'maps' folder: blocks/TASK.trix -> maps/TASK.map.yaml
    """
    titl = parse_trix(matrix_path).titl
    candidates = [
        matrix_path.with_suffix(".map.yaml"),
        matrix_path.with_suffix(".map.yml"),
        matrix_path.parent.parent / "maps" / f"{titl}.map.yaml",
        matrix_path.parent.parent / "maps" / f"{titl}.map.yml",
    ]
    for c in candidates:
        if c.exists():
            return yaml.safe_load(c.read_text(encoding="utf-8"))
    return None


def build_matrix_record(matrix_path: Path) -> MatrixRecord:
    m = parse_trix(matrix_path)
    errs = validate_block_3x3(m)
    if errs:
        raise ValueError("\n".join(errs))

    mapping = load_map_for_matrix(matrix_path) or {}
    cell_map = (mapping.get("cells") or {})

    cells: List[CellBinding] = []
    for slot, r, c, token in m.slots_3x3():
        payload = cell_map.get(str(token)) or cell_map.get(str(slot)) or {}
        kind = payload.get("kind") if isinstance(payload, dict) else None

        if not kind:
            if isinstance(payload, dict) and "node_id" in payload:
                kind = "node"
            elif payload:
                kind = "unknown"
            else:
                kind = "empty"

        cells.append(CellBinding(
            kind=str(kind),
            token=str(token),
            slot=int(slot),
            row=int(r),
            col=int(c),
            payload=payload if isinstance(payload, dict) else {"value": payload},
        ))

    return MatrixRecord(titl=m.titl, path=str(matrix_path), skin_hint=m.skin_hint, cells=cells)


def index_repo(root: Path) -> Dict[str, Any]:
    """Walk a directory tree for .trix files and build a geometry-preserving index."""
    matrices: Dict[str, Any] = {}
    nodes: Dict[str, Any] = {}

    for p in root.rglob("*.trix"):
        rec = build_matrix_record(p)
        matrices[rec.titl] = {
            "titl": rec.titl,
            "path": rec.path,
            "skin": rec.skin_hint,
            "cells": [
                {
                    "slot": c.slot,
                    "row": c.row,
                    "col": c.col,
                    "token": c.token,
                    "kind": c.kind,
                    "payload": c.payload,
                }
                for c in rec.cells
            ],
        }

        for c in rec.cells:
            if c.kind != "node":
                continue
            node_id = c.payload.get("node_id")
            if not node_id:
                continue
            nodes.setdefault(node_id, {
                "node_id": node_id,
                "bindings": [],
                "facets": {},
            })
            nodes[node_id]["bindings"].append({
                "matrix": rec.titl,
                "slot": c.slot,
                "token": c.token,
                "path": rec.path,
            })
            nodes[node_id]["facets"].update(c.payload.get("facets", {}))

    return {"matrices": matrices, "nodes": nodes}


def save_index(index: Dict[str, Any], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(index, indent=2), encoding="utf-8")
