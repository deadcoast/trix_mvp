#!/usr/bin/env python3
"""Binding and facet resolution helpers for pin/content commands."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from .trix_gutters import _guttered_vlg_hlg_to_lc, _parse_lc
except ImportError:  # pragma: no cover
    from trix_gutters import _guttered_vlg_hlg_to_lc, _parse_lc

try:
    import yaml as yaml_module  # type: ignore
except ImportError:  # pragma: no cover
    yaml_module = None


def _safe_load_yaml(path: Path) -> Dict[str, Any]:
    """Load a YAML mapping from disk."""
    if yaml_module is None:
        raise RuntimeError("PyYAML is not available; cannot load .map.yaml")
    data = yaml_module.safe_load(path.read_text(encoding="utf-8", errors="replace")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected YAML mapping at root")
    return data


def _find_map_for_titl(repo_root: Path, titl: str) -> Optional[Path]:
    """Find the most likely .map.yaml file for a given titl."""
    candidates = list(repo_root.rglob(f"{titl}.map.yaml"))
    candidates += list(repo_root.rglob(f"{titl}.map.yml"))
    if not candidates:
        return None

    def score(p: Path) -> Tuple[int, int]:
        parts = [s.lower() for s in p.parts]
        return (0 if "maps" in parts else 1, len(p.parts))

    return sorted(set(candidates), key=score)[0]


def _resolve_cell_binding(
    map_doc: Dict[str, Any],
    slot: int,
    token: Optional[int],
) -> Optional[Dict[str, Any]]:
    """Resolve a binding payload for a slot/token from a .map.yaml."""
    cells = map_doc.get("cells")
    if not isinstance(cells, dict):
        return None

    keys = [str(slot)]
    if token is not None:
        keys.insert(0, str(token))
    for key in keys:
        val = cells.get(key)
        if isinstance(val, dict):
            return val
    return None


def _read_facet_payload(
    repo_root: Path,
    map_path: Path,
    facet_path: str,
    *,
    full: bool,
    max_chars: int,
) -> Dict[str, Any]:
    """Load facet content or excerpt for a bound node facet."""
    p = Path(facet_path)
    candidates = [repo_root / p, map_path.parent / p]
    for cand in candidates:
        if cand.exists() and cand.is_file():
            txt = cand.read_text(encoding="utf-8", errors="replace")
            try:
                rel = cand.relative_to(repo_root)
                path_str = str(rel)
            except ValueError:
                path_str = str(cand)
            payload: Dict[str, Any] = {"path": path_str}
            if full:
                payload["content"] = txt
            else:
                payload["excerpt"] = txt[:max_chars]
                if len(txt) > max_chars:
                    payload["truncated"] = True
            return payload
    return {"path": facet_path, "missing": True}


def resolve_pin_to_binding(
    repo_root: Path,
    *,
    titl: str,
    slot: int,
    token: Optional[int],
    full: bool = False,
    max_chars: int = 1400,
    facet_filter: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Resolve a pin to its map binding and facet payloads."""
    out: Dict[str, Any] = {
        "titl": titl,
        "slot": slot,
        "token": token,
        "map": None,
        "binding": None,
    }

    map_path = _find_map_for_titl(repo_root, titl)
    if not map_path:
        out["map"] = {"found": False}
        return out

    try:
        map_rel = str(map_path.relative_to(repo_root))
    except ValueError:
        map_rel = str(map_path)
    out["map"] = {"found": True, "path": map_rel}
    map_doc = _safe_load_yaml(map_path)
    binding = _resolve_cell_binding(map_doc, slot=slot, token=token)
    if not binding:
        return out

    out["binding"] = binding

    facets = binding.get("facets")
    if isinstance(facets, dict):
        facet_payloads: Dict[str, Any] = {}
        for k, v in facets.items():
            if facet_filter and str(k) not in facet_filter:
                continue
            if isinstance(v, str):
                facet_payloads[str(k)] = _read_facet_payload(
                    repo_root,
                    map_path,
                    v,
                    full=full,
                    max_chars=max_chars,
                )
        out["facets"] = facet_payloads
    return out


def _resolve_pin_location(
    *,
    lines: List[str],
    lc: Optional[str],
    line: Optional[int],
    col: Optional[int],
    vlg: Optional[int],
    hlg: Optional[int],
) -> Tuple[int, int, Dict[str, Any]]:
    """Resolve pin input args into an absolute (line, col) and metadata."""
    if lc:
        line_num, col_num = _parse_lc(lc)
        return line_num, col_num, {"lc": lc, "line": line_num, "col": col_num}
    if line is not None and col is not None:
        return int(line), int(col), {"line": int(line), "col": int(col)}
    if vlg is not None and hlg is not None:
        line_num, col_num = _guttered_vlg_hlg_to_lc(lines, int(vlg), int(hlg))
        return (
            line_num,
            col_num,
            {"vlg": int(vlg), "hlg": int(hlg), "line": line_num, "col": col_num},
        )
    raise SystemExit("pin/content requires either --lc, --line/--col, or --vlg/--hlg")


def _parse_facet_filter(raw: Optional[List[str]]) -> Optional[List[str]]:
    """Normalize facet filter inputs into a list of facet names."""
    if not raw:
        return None
    facets: List[str] = []
    for item in raw:
        facets.extend([p for p in item.split(",") if p])
    return facets or None
