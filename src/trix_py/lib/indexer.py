"""Geometry-first indexer for .trix files and their bindings."""

from __future__ import annotations

import json
import yaml

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, cast

from .parser import parse_trix, validate_block_3x3 as validate_trix_block_3x3


@dataclass
class CellBinding:
    """Binding and geometry for a single cell."""

    cell_id: str
    block: str
    slot: int
    row: int
    col: int
    binding: Optional[Dict[str, Any]]
    kind: str
    token: str
    payload: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the binding as a dict."""
        return {
            "cell_id": self.cell_id,
            "block": self.block,
            "slot": self.slot,
            "row": self.row,
            "col": self.col,
            "binding": self.binding,
            "kind": self.kind,
            "token": self.token,
            "payload": self.payload,
        }


@dataclass
class MatrixRecord:
    """Parsed matrix record with bindings."""

    titl: str
    path: Path
    skin_hint: Optional[str]
    cells: List[CellBinding]
    skin: Optional[Path] = None

    @classmethod
    def from_json(cls, s: str) -> "MatrixRecord":
        """Construct from a JSON string."""
        return cls.from_dict(json.loads(s))

    @classmethod
    def from_yaml(cls, s: str) -> "MatrixRecord":
        """Construct from a YAML string."""
        return cls.from_dict(yaml.safe_load(s))

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MatrixRecord":
        """Construct a MatrixRecord from a dictionary."""
        path = Path(data["path"])
        if not path.is_absolute():
            path = Path.cwd() / path

        skin_value = data.get("skin")
        skin_path: Optional[Path] = None
        if skin_value:
            skin_path = Path(skin_value)
            if not skin_path.is_absolute():
                skin_path = Path.cwd() / skin_path

        if not path.is_file():
            raise ValueError(f"File not found: {path}")
        if skin_path and not skin_path.is_file():
            raise ValueError(f"File not found: {skin_path}")

        cells_raw = data.get("cells")
        if not isinstance(cells_raw, list):
            raise TypeError("cells must be a list")

        cells: List[CellBinding] = []
        for cell in cells_raw:
            if not isinstance(cell, dict) or not all(isinstance(key, str) for key in cell):
                raise TypeError("cells must be a list of dicts with string keys")
            cells.append(CellBinding(**cast(Dict[str, Any], cell)))
        if not cells:
            raise ValueError(f"No cells found in {path}")

        if not validate_block_3x3(cells):
            raise ValueError(f"Invalid block in {path}")

        titl = data.get("titl") or path.stem
        skin_hint = data.get("skin_hint")

        return cls(
            titl=titl,
            path=path,
            skin_hint=skin_hint,
            cells=cells,
            skin=skin_path,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the record as a dict."""
        return {
            "titl": self.titl,
            "path": str(self.path),
            "skin_hint": self.skin_hint,
            "cells": [c.to_dict() for c in self.cells],
            "skin": str(self.skin) if self.skin else None,
        }

    def to_json(self) -> str:
        """Serialize the record as JSON."""
        return json.dumps(self.to_dict())

    def to_yaml(self) -> str:
        """Serialize the record as YAML."""
        return yaml.safe_dump(self.to_dict())


def validate_block_3x3(cells: Sequence[CellBinding]) -> bool:
    """Validate a 3x3 grid using cell row/col coordinates."""
    if len(cells) != 9:
        return False

    coords = {(cell.row, cell.col) for cell in cells}
    if len(coords) != 9:
        return False

    rows = sorted({row for row, _ in coords})
    cols = sorted({col for _, col in coords})
    if rows not in ([0, 1, 2], [1, 2, 3]) or cols not in ([0, 1, 2], [1, 2, 3]):
        return False

    expected = {(row, col) for row in rows for col in cols}
    return coords == expected


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
    return next(
        (yaml.safe_load(c.read_text(encoding="utf-8")) for c in candidates if c.exists()),
        None,
    )


def build_matrix_record(matrix_path: Path) -> MatrixRecord:
    """Build a MatrixRecord from a .trix file and its mapping."""
    m = parse_trix(matrix_path)
    if errs := validate_trix_block_3x3(m):
        raise ValueError("\n".join(errs))

    mapping = load_map_for_matrix(matrix_path) or {}
    cell_map = mapping.get("cells") or {}

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

        cells.append(
            CellBinding(
                cell_id=f"{m.titl}-{slot}",
                block=m.titl,
                slot=int(slot),
                row=int(r),
                col=int(c),
                binding=payload if isinstance(payload, dict) else None,
                kind=str(kind),
                token=str(token),
                payload=payload if isinstance(payload, dict) else {"value": payload},
            )
        )

    return MatrixRecord(
        titl=m.titl,
        path=matrix_path,
        skin_hint=m.skin_hint,
        cells=cells,
        skin=None,
    )


def index_repo(root: Path) -> Dict[str, Any]:
    """Walk a directory tree for .trix files and build a geometry-preserving index."""
    matrices: Dict[str, Any] = {}
    nodes: Dict[str, Any] = {}

    for p in root.rglob("*.trix"):
        rec = build_matrix_record(p)
        matrices[rec.titl] = {
            "titl": rec.titl,
            "path": str(rec.path),
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
            nodes.setdefault(
                node_id,
                {
                    "node_id": node_id,
                    "bindings": [],
                    "facets": {},
                },
            )
            nodes[node_id]["bindings"].append(
                {
                    "matrix": rec.titl,
                    "slot": c.slot,
                    "token": c.token,
                    "path": str(rec.path),
                }
            )
            nodes[node_id]["facets"].update(c.payload.get("facets", {}))

    return {"matrices": matrices, "nodes": nodes}


def save_index(index: Dict[str, Any], out_path: Path) -> None:
    """Write the index to disk as JSON."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(index, indent=2), encoding="utf-8")
