#!/usr/bin/env python3
"""Operator validation helpers for junction canvases."""

from __future__ import annotations

import json
import re

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple


try:
    import yaml as yaml_module  # type: ignore
except ImportError:  # pragma: no cover
    yaml_module = None


@dataclass(frozen=True)
class OperatorExpectation:
    """Expected operator placement within a vlg/hlg region."""

    rule: Optional[str]
    operator: str
    vlg0: int
    vlg1: int
    hlg0: int
    hlg1: int


def _parse_range(part: str) -> Tuple[int, int]:
    """Parse a range like '3' or '3->5' into (start, end)."""
    part = part.strip()
    if "->" in part:
        a, b = part.split("->", 1)
        return int(a), int(b)
    return int(part), int(part)


def _parse_range_value(value: object) -> Optional[Tuple[int, int]]:
    """Parse a range from a scalar value."""
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value, value
    if isinstance(value, str):
        try:
            return _parse_range(value)
        except ValueError:
            return None
    return None


def _coerce_int(value: object) -> Optional[int]:
    """Coerce a value to int if possible."""
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip():
        try:
            return int(value)
        except ValueError:
            return None
    return None


def _parse_coord_token(token: str) -> List[Tuple[int, int, int, int]]:
    """Parse a vlg/hlg token like '10->12/05->07'."""
    token = token.strip()
    if not token or "/" not in token:
        return []
    vlg_part, hlg_part = token.split("/", 1)
    try:
        h0, h1 = _parse_range(hlg_part)
    except ValueError:
        return []
    v_ranges = [p.strip() for p in vlg_part.split("&")]
    coords = []
    for vr in v_ranges:
        if not vr:
            continue
        try:
            v0, v1 = _parse_range(vr)
        except ValueError:
            continue
        coords.append((v0, v1, h0, h1))
    return coords


def parse_operator_summary(text: str) -> Tuple[List[OperatorExpectation], List[str]]:
    """Parse the Operator Summary table from a junction document."""
    lines = text.splitlines()
    start_idx = None
    for i, line in enumerate(lines):
        if line.strip().lower().startswith("| rule | operator |"):
            start_idx = i + 2  # skip header + separator
            break
    if start_idx is None:
        return [], ["Operator Summary table not found"]

    expected: List[OperatorExpectation] = []
    skipped: List[str] = []
    for line in lines[start_idx:]:
        if not line.strip().startswith("|"):
            break
        parts = [p.strip() for p in line.strip().split("|")[1:-1]]
        if len(parts) < 4:
            continue
        rule, operator, _meaning, coord_text = parts[:4]
        op = operator.strip("` ").strip()
        if not coord_text:
            continue
        tokens = [t.strip() for t in coord_text.split(",") if t.strip()]
        for token in tokens:
            coords = _parse_coord_token(token)
            if not coords:
                skipped.append(f"{rule}:{op}:{token}")
                continue
            expected.extend(
                [
                    OperatorExpectation(
                        rule=rule or None,
                        operator=op,
                        vlg0=v0,
                        vlg1=v1,
                        hlg0=h0,
                        hlg1=h1,
                    )
                    for v0, v1, h0, h1 in coords
                ]
            )
    return expected, skipped


def _safe_load_yaml(path: Path) -> Dict[str, Any]:
    """Load a YAML mapping file from disk."""
    if yaml_module is None:
        raise RuntimeError("PyYAML is not available; cannot load YAML spec")
    data = yaml_module.safe_load(path.read_text(encoding="utf-8", errors="replace")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected YAML mapping at root")
    return data


def load_expectations(spec_path: Path) -> List[OperatorExpectation]:
    """Load operator expectations from a YAML or JSON spec file."""
    if spec_path.suffix.lower() == ".json":
        data = json.loads(spec_path.read_text(encoding="utf-8", errors="replace"))
    else:
        data = _safe_load_yaml(spec_path)

    ops = data.get("operators") if isinstance(data, dict) else data
    if not isinstance(ops, list):
        raise ValueError("spec must be a list or include an 'operators' list")

    expected: List[OperatorExpectation] = []
    for entry in ops:
        if not isinstance(entry, dict):
            continue
        op = str(entry.get("operator", "")).strip()
        if not op:
            continue
        rule = str(entry.get("rule", "")).strip() or None
        coords = entry.get("coords") or []
        if not isinstance(coords, list):
            continue
        for coord in coords:
            if not isinstance(coord, dict):
                continue
            v = _parse_range_value(coord.get("vlg"))
            if not v:
                continue
            h_raw = coord.get("hlg")
            if isinstance(h_raw, list) and len(h_raw) == 2:
                h0 = _coerce_int(h_raw[0])
                h1 = _coerce_int(h_raw[1])
                if h0 is None or h1 is None:
                    continue
                h = (h0, h1)
            else:
                h = _parse_range_value(h_raw)
                if not h:
                    continue
            v0, v1 = v
            h0, h1 = h
            expected.append(
                OperatorExpectation(
                    rule=rule,
                    operator=op,
                    vlg0=v0,
                    vlg1=v1,
                    hlg0=h0,
                    hlg1=h1,
                )
            )
    return expected


def _operator_pattern(operator: str) -> re.Pattern[str]:
    """Return a regex that matches a rendered operator glyph."""
    op = operator.strip("` ").strip()
    patterns = {
        "(+)": r"\(\+\)",
        "[-]": r"\[-\]",
        "-|-": r"\|\-\|\-\|",
        "~": r"~\|~",
        "+": r"\| \+ \|",
        "-": r"\| - \|",
        "[| |]": r"\[\| \|\]",
        "[//]": r"\[//\]",
        "%": r"%",
    }
    return re.compile(patterns.get(op, re.escape(op)))


def validate_expectations(
    text: str,
    expected: Sequence[OperatorExpectation],
    extract_region: Callable[[str, int, int, int, int], Dict[str, Any]],
) -> Dict[str, Any]:
    """Validate operator placements using the provided region extractor."""
    errors: List[Dict[str, Any]] = []
    checked = 0
    for entry in expected:
        operator = entry.operator
        region = extract_region(text, entry.vlg0, entry.vlg1, entry.hlg0, entry.hlg1)
        rows = region.get("rows") if isinstance(region, dict) else []
        row_slices = []
        if isinstance(rows, list):
            for row in rows:
                if isinstance(row, dict):
                    row_slices.append(str(row.get("slice", "")))
        region_text = "\n".join(row_slices)
        pattern = _operator_pattern(operator)
        checked += 1
        if not pattern.search(region_text):
            errors.append(
                {
                    "operator": operator,
                    "rule": entry.rule,
                    "vlg": [entry.vlg0, entry.vlg1],
                    "hlg": [entry.hlg0, entry.hlg1],
                    "region": region_text,
                }
            )
    return {"checked": checked, "errors": errors}
