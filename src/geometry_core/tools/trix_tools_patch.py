#!/usr/bin/env python3
"""
TRIX Unified Tools (v0.1)

Goal: stitch together the *semantic* index (.trix + .map.yaml -> facets)
with the *geometry/junction* index (embedded matrices + pinpoint coords).

This does NOT flatten TRIX into links. It preserves:
- geometry (matrix + slot + junction coords)
- bindings (node_id + facets)
- context bundling (load facets on demand)

Usage examples:

  # Build a combined index for the whole repo
  python tools/trix_unified.py unified-index --repo . --out .index/trix_unified.json

  # Resolve a coordinate in a junction and print an agent-ready context bundle
  python tools/trix_unified.py context-at src/geometry_core/examples/junctions/matrix_junction_example.md --line 2 --col 8 --repo .

  # Same, but using native vlg/hlg gutters (as in matrix_junction.md)
  python tools/trix_unified.py context-at src/geometry_core/matrix_junction.md --vlg 8 --hlg 9 --repo .
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module {name} from {path}")
    mod = importlib.util.module_from_spec(spec)
    # dataclasses (and some stdlib internals) assume the module is present in sys.modules
    import sys
    sys.modules[name] = mod
    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    return mod



def _semantic_index(repo: Path, semantic_root: Optional[Path] = None) -> Dict[str, Any]:
    """Use src/trix_py indexer to build the semantic index (matrices + nodes)."""
    trix_py = repo / "src" / "trix_py"
    if not trix_py.exists():
        raise FileNotFoundError("Expected src/trix_py to exist.")
    # Put src/trix_py on sys.path so imports work
    import sys
    if str(trix_py) not in sys.path:
        sys.path.insert(0, str(trix_py))

    from lib.indexer import index_repo  # type: ignore

    root = (semantic_root or repo).resolve()
    return index_repo(root)


def _geometry_module(repo: Path):
    """Load src/geometry_core/tools/trix.py as an importable module."""
    path = repo / "src" / "geometry_core" / "tools" / "trix.py"
    if not path.exists():
        raise FileNotFoundError(f"Expected geometry tool at {path}")
    return _load_module("trix_geometry_tool", path)


def _try_read(path: Path) -> Optional[str]:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None


def _scan_junction_files(repo: Path) -> Dict[str, Any]:
    """Scan all .md/.txt files and keep the ones that contain embedded 3×3 blocks."""
    geom = _geometry_module(repo)

    out: Dict[str, Any] = {}
    for p in repo.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix.lower() not in {".md", ".txt"}:
            continue
        txt = _try_read(p)
        if not txt:
            continue
        # quick heuristic to avoid scanning everything
        if "==[" not in txt and "| ==[" not in txt:
            continue
        try:
            embedded = geom.scan_junction(txt)
        except Exception:
            continue
        if not embedded:
            continue
        out[str(p)] = {
            "path": str(p),
            "embedded": [
                {
                    "titl": e.titl,
                    "anchor_line": e.anchor_line,
                    "anchor_col": e.anchor_col,
                    "bbox": {"l0": e.bbox[0], "c0": e.bbox[1], "l1": e.bbox[2], "c1": e.bbox[3]},
                    "skin": getattr(e.block, "skin", None),
                    "cells": [asdict(c) for c in e.block.cells],
                }
                for e in embedded
            ],
        }
    return out


def _join_binding(semantic: Dict[str, Any], titl: str, slot: int) -> Optional[Dict[str, Any]]:
    m = semantic.get("matrices", {}).get(titl)
    if not m:
        return None
    # find the matching cell record
    for c in m.get("cells", []):
        if int(c.get("slot")) == int(slot):
            return c
    return None


def _load_facets(repo: Path, facets: Dict[str, str]) -> Dict[str, str]:
    loaded: Dict[str, str] = {}
    for k, rel in facets.items():
        p = (repo / rel).resolve() if not Path(rel).is_absolute() else Path(rel)
        txt = _try_read(p)
        if txt is None:
            loaded[k] = f"<<missing facet file: {rel}>>"
        else:
            loaded[k] = txt
    return loaded


def cmd_unified_index(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    out_path = Path(args.out).resolve()

    semantic_root = (repo / args.semantic_root) if args.semantic_root else repo
    semantic = _semantic_index(repo, semantic_root=semantic_root)
    junctions = _scan_junction_files(repo)

    # Join bindings into junction cell records (non-destructive add)
    for j in junctions.values():
        for e in j["embedded"]:
            titl = e.get("titl")
            if not titl:
                continue
            for c in e.get("cells", []):
                bind = _join_binding(semantic, titl, int(c["slot"]))
                if bind:
                    c["binding"] = bind

    combined = {
        "repo": str(repo),
        "semantic": semantic,
        "junctions": junctions,
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(combined, indent=2), encoding="utf-8")
    print(f"Wrote unified index: {out_path}")
    print(f"- semantic matrices: {len(semantic.get('matrices', {}))}")
    print(f"- semantic nodes:    {len(semantic.get('nodes', {}))}")
    print(f"- junction files:    {len(junctions)}")
    return 0


def _resolve_lc_from_args(repo: Path, text: str, args: argparse.Namespace) -> Tuple[int, int]:
    if args.line is not None and args.col is not None:
        return int(args.line), int(args.col)

    if args.vlg is not None and args.hlg is not None:
        geom = _geometry_module(repo)
        lines = geom.normalize_lines(text)
        return geom._guttered_vlg_hlg_to_lc(lines, int(args.vlg), int(args.hlg))  # type: ignore[attr-defined]

    raise ValueError("Provide either (--line and --col) OR (--vlg and --hlg).")


def cmd_context_at(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    path = Path(args.path).resolve()
    txt = _try_read(path)
    if txt is None:
        raise FileNotFoundError(path)

    semantic_root = (repo / args.semantic_root) if args.semantic_root else repo
    semantic = _semantic_index(repo, semantic_root=semantic_root)
    geom = _geometry_module(repo)

    line, col = _resolve_lc_from_args(repo, txt, args)
    hit = geom.resolve_coordinate(txt, line=line, col=col)["hit"]
    titl = hit.get("matrix")
    slot = hit.get("slot")

    bundle: Dict[str, Any] = {
        "source": {"path": str(path), "line": line, "col": col},
        "resolved": hit,
        "binding": None,
        "node": None,
        "facets": None,
    }

    if titl and slot:
        binding = _join_binding(semantic, str(titl), int(slot))
        bundle["binding"] = binding
        if binding and binding.get("kind") == "node":
            node_id = (binding.get("payload") or {}).get("node_id")
            if node_id:
                node = semantic.get("nodes", {}).get(node_id)
                bundle["node"] = node
                facets = (binding.get("payload") or {}).get("facets") or {}
                bundle["facets"] = _load_facets(repo, facets)

    if args.format == "json":
        print(json.dumps(bundle, indent=2))
    else:
        # markdown view
        print(f"# TRIX context-at")
        print()
        print(f"- file: `{path}`")
        print(f"- coordinate: L{line} C{col}")
        print(f"- resolved: `{bundle['resolved'].get('address')}`")
        print()
        if bundle["binding"] is None:
            print("No semantic binding found for this matrix/slot.")
            return 0
        print("## Binding")
        print("```json")
        print(json.dumps(bundle["binding"], indent=2))
        print("```")
        if bundle["node"] is not None:
            print("## Node")
            print("```json")
            print(json.dumps(bundle["node"], indent=2))
            print("```")
        if bundle["facets"] is not None:
            print("## Facets")
            for k, v in bundle["facets"].items():
                print()
                print(f"### {k}")
                print("```md")
                # keep it readable, but do not truncate aggressively
                print(v.strip())
                print("```")

    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="trix-unified")
    sub = p.add_subparsers(dest="cmd", required=True)

    ui = sub.add_parser("unified-index", help="build a combined semantic+junction index JSON")
    ui.add_argument("--repo", default=".")
    ui.add_argument("--semantic-root", default="examples", help="path (relative to --repo) to index for semantic .trix + .map.yaml truth")
    ui.add_argument("--out", required=True)
    ui.set_defaults(func=cmd_unified_index)

    ca = sub.add_parser("context-at", help="resolve a coordinate in a junction and print a context bundle")
    ca.add_argument("path")
    ca.add_argument("--repo", default=".")
    ca.add_argument("--semantic-root", default="examples", help="path (relative to --repo) to index for semantic .trix + .map.yaml truth")
    ca.add_argument("--format", choices=["json", "md"], default="md")
    ca.add_argument("--line", type=int)
    ca.add_argument("--col", type=int)
    ca.add_argument("--vlg", type=int)
    ca.add_argument("--hlg", type=int)
    ca.set_defaults(func=cmd_context_at)

    return p


def main() -> int:
    p = build_parser()
    args = p.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
