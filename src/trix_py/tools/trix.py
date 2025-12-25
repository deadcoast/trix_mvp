#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Ensure repo root is on sys.path so `lib.*` imports work when running from /tools
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from lib.parser import parse_trix, validate_block_3x3
from lib.indexer import build_matrix_record, index_repo, save_index


def cmd_parse(args: argparse.Namespace) -> int:
    m = parse_trix(args.file)
    print(
        json.dumps(
            {
                "titl": m.titl,
                "skin_hint": m.skin_hint,
                "cells": m.raw_cells,
            },
            indent=2,
        )
    )
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    m = parse_trix(args.file)
    if errs := validate_block_3x3(m):
        print("\n".join(errs))
        return 2
    print(f"OK: {m.titl} ({args.file})")
    return 0


def cmd_index(args: argparse.Namespace) -> int:
    root = Path(args.root)
    idx = index_repo(root)
    out = Path(args.out)
    save_index(idx, out)
    print(f"Wrote index: {out}")
    print(f"Matrices: {len(idx['matrices'])}, Nodes: {len(idx['nodes'])}")
    return 0


def cmd_zoom(args: argparse.Namespace) -> int:
    rec = build_matrix_record(Path(args.file))
    cell = next(
        (c for c in rec.cells if c.slot == args.cell or str(c.token) == str(args.cell)),
        None,
    )
    if not cell:
        print(f"No such cell: {args.cell}")
        return 2

    print(
        json.dumps(
            {
                "matrix": rec.titl,
                "cell": {
                    "slot": cell.slot,
                    "token": cell.token,
                    "kind": cell.kind,
                    "payload": cell.payload,
                },
            },
            indent=2,
        )
    )
    return 0


def cmd_context(args: argparse.Namespace) -> int:
    rec = build_matrix_record(Path(args.file))
    cell = next(
        (c for c in rec.cells if c.slot == args.cell or str(c.token) == str(args.cell)),
        None,
    )
    if not cell:
        print(f"No such cell: {args.cell}")
        return 2

    bundle = {
        "matrix": rec.titl,
        "slot": cell.slot,
        "row": cell.row,
        "col": cell.col,
        "token": cell.token,
        "kind": cell.kind,
        "payload": cell.payload,
        "facets": {},
    }

    facets = (
        (cell.payload.get("facets") or {}) if isinstance(cell.payload, dict) else {}
    )
    for facet_name, rel_path in facets.items():
        p = (Path(args.repo) / rel_path).resolve()
        if p.exists():
            bundle["facets"][facet_name] = {
                "path": str(rel_path),
                "content": p.read_text(encoding="utf-8", errors="replace"),
            }
        else:
            bundle["facets"][facet_name] = {
                "path": str(rel_path),
                "missing": True,
            }

    print(json.dumps(bundle, indent=2))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="trix", description="TRIX geometry-first parser/indexer"
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("parse", help="Parse a .trix file into a canonical AST (JSON).")
    p.add_argument("file")
    p.set_defaults(fn=cmd_parse)

    v = sub.add_parser("validate", help="Validate a .trix 3x3 block.")
    v.add_argument("file")
    v.set_defaults(fn=cmd_validate)

    i = sub.add_parser("index", help="Index a directory of .trix files.")
    i.add_argument("root")
    i.add_argument("--out", default=".index/trix_index.json")
    i.set_defaults(fn=cmd_index)

    z = sub.add_parser("zoom", help="Inspect one cell binding (geometry preserved).")
    z.add_argument("file")
    z.add_argument(
        "--cell",
        type=int,
        required=True,
        help="Slot number 1..9 (or token if numeric).",
    )
    z.set_defaults(fn=cmd_zoom)

    c = sub.add_parser(
        "context", help="Build an agent context bundle for a cell (includes facets)."
    )
    c.add_argument("file")
    c.add_argument("--cell", type=int, required=True)
    c.add_argument("--repo", default=".", help="Repo root for resolving facet paths.")
    c.set_defaults(fn=cmd_context)

    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
