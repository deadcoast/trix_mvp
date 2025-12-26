#!/usr/bin/env python3
"""Gutter and coordinate helpers for junction canvases."""

from __future__ import annotations

import re

from pathlib import Path
from typing import Any, Dict, List, Tuple


def read_text(path: Path) -> str:
    """Read a text file with UTF-8 decoding and replacement."""
    return path.read_text(encoding="utf-8", errors="replace")


def normalize_lines(text: str) -> List[str]:
    """Normalize tabs to spaces and split into lines."""
    # Normalize tabs to spaces for stable column indexing
    text = text.replace("\t", "    ")
    return text.splitlines()


def gutter_overlay(text: str, start_line: int = 0) -> str:
    """Overlay L#### and C#### gutters on any text."""
    lines = normalize_lines(text)
    maxlen = max((len(line_text) for line_text in lines), default=0)

    ones = "".join(str(i % 10) for i in range(maxlen))
    tens = "".join(str((i // 10) % 10) if i % 10 == 0 else " " for i in range(maxlen))
    hund = "".join(str((i // 100) % 10) if i % 100 == 0 else " " for i in range(maxlen))

    out = [f"     C:{hund}", f"     C:{tens}", f"     C:{ones}"]
    out.extend(f"L{start_line + idx:04d} {line}" for idx, line in enumerate(lines))
    return "\n".join(out) + "\n"


def _parse_lc(arg: str) -> Tuple[int, int]:
    """Parse 'L####:C####' (or 'L42:C137') into (line, col)."""
    if m := re.match(r"L(\d+):C(\d+)", arg.strip(), flags=re.I):
        return int(m[1]), int(m[2])
    raise ValueError("Expected format L####:C####")


def _guttered_vlg_hlg_to_lc(lines: List[str], vlg: int, hlg: int) -> Tuple[int, int]:
    """Convert (vlg, hlg) from the native junction gutter grid into text (line, col)."""
    row_line = None
    for i, line_text in enumerate(lines):
        m = re.match(r"\|(\d{2})\|", line_text)
        if not m:
            continue
        if int(m[1]) == vlg:
            row_line = i
            break
    if row_line is None:
        raise ValueError(f"Could not find vlg row {vlg:02d} in file")

    hlabel_idx = next(
        (i for i, line_text in enumerate(lines) if re.match(r"\|01\|02\|", line_text)),
        None,
    )
    if hlabel_idx is None:
        raise ValueError("Could not find horizontal gutter line starting with '|01|02|'")

    hlabel = lines[hlabel_idx]
    bars = [m.start() for m in re.finditer(r"\|", hlabel)]
    if hlg < 1 or hlg >= len(bars):
        raise ValueError(f"hlg must be 1..{len(bars) - 1}, got {hlg}")

    x0 = bars[hlg - 1] + 1
    x1 = bars[hlg] - 1
    col = (x0 + x1) // 2
    return row_line, col


def extract_region_vlg_hlg(
    text: str,
    vlg0: int,
    vlg1: int,
    hlg0: int,
    hlg1: int,
) -> Dict[str, Any]:
    """Extract a rectangular region from a native-gutter junction canvas (vlg/hlg)."""
    lines = normalize_lines(text)

    hlabel_idx = next(
        (i for i, line_text in enumerate(lines) if re.match(r"\|01\|02\|", line_text)),
        None,
    )
    if hlabel_idx is None:
        raise ValueError("Could not find horizontal gutter line starting with '|01|02|'")

    hlabel = lines[hlabel_idx]
    bars = [m.start() for m in re.finditer(r"\|", hlabel)]
    if hlg0 < 1 or hlg1 < 1 or hlg0 >= len(bars) or hlg1 >= len(bars):
        raise ValueError(f"hlg must be 1..{len(bars) - 1}")

    hmin, hmax = min(hlg0, hlg1), max(hlg0, hlg1)
    x0 = bars[hmin - 1] + 1
    x1 = bars[hmax] - 1

    v_to_line: Dict[int, int] = {}
    for i, line_text in enumerate(lines):
        if m := re.match(r"\|(\d{2})\|", line_text):
            v_to_line[int(m[1])] = i

    vmin, vmax = min(vlg0, vlg1), max(vlg0, vlg1)
    if missing := [v for v in range(vmin, vmax + 1) if v not in v_to_line]:
        raise ValueError(f"Missing vlg rows: {missing}")

    rows = []
    for v in range(vmax, vmin - 1, -1):
        li = v_to_line[v]
        rows.append(
            {
                "vlg": v,
                "line": li,
                "slice": lines[li][x0 : x1 + 1],
            }
        )

    return {
        "vlg": [vmin, vmax],
        "hlg": [hmin, hmax],
        "x0": x0,
        "x1": x1,
        "rows": rows,
    }
