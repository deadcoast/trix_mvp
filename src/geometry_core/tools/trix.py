#!/usr/bin/env python3
"""
TRIX geometry-first helper tools (v0.3)

Goals:
- preserve matrix geometry (cells + coordinates)
- support gutters for pinpoint references (L/C)
- parse common skins by extracting:
  - TITL ([ABCD])
  - the 3x3 numeric slots [1]..[9]
- scan "junction" canvases for multiple embedded matrices

This is intentionally lightweight and repo-agnostic. It is meant to be dropped
into your TRIX repo and extended.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple


CELL_RE = re.compile(r"\[(\s*[1-9]\s*)\]")
TITL_RE = re.compile(r"\[([A-Za-z0-9]{4})\]")  # strict 4-char title token


def slot_to_rc(slot: int) -> Tuple[int, int]:
    if slot < 1 or slot > 9:
        raise ValueError("slot must be 1..9")
    r = (slot - 1) // 3 + 1
    c = (slot - 1) % 3 + 1
    return r, c


def rc_to_slot(r: int, c: int) -> int:
    if r < 1 or r > 3 or c < 1 or c > 3:
        raise ValueError("row/col must be 1..3 for a 3x3 block")
    return (r - 1) * 3 + c


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def normalize_lines(text: str) -> List[str]:
    # Normalize tabs to spaces for stable column indexing
    text = text.replace("\t", "    ")
    return text.splitlines()


def detect_titl(text: str) -> Optional[str]:
    # Title is first [ABCD] that is not numeric [1]..[9]
    for m in TITL_RE.finditer(text):
        token = m.group(1)
        # Exclude numeric 1..9
        if not token.isdigit():
            return token
    return None


@dataclass
class ParsedBlock:
    titl: Optional[str]
    rows: List[List[int]]  # 3 rows, 3 cols
    row_lines: List[int]   # line indices where each row was found
    skin: Optional[str] = None


def guess_skin(lines: List[str]) -> Optional[str]:
    joined = "\n".join(lines[:8])
    if "| ==[" in joined and "| - [" in joined:
        return "clunk"
    if "= ==[" in joined and "| [1]" in joined:
        return "fcy"
    if re.search(r"^==\[[A-Za-z0-9]{4}\]", joined, flags=re.M):
        return "prth_or_boring"
    return None


def parse_first_block(text: str) -> ParsedBlock:
    """
    Extract the first 3 consecutive lines that each contain exactly 3 numeric cells [1]..[9].
    This works for most skins because decoration is ignored.
    """
    lines = normalize_lines(text)
    titl = detect_titl(text)
    skin = guess_skin(lines)

    # Find candidate lines containing exactly 3 numeric cell tokens.
    candidate: List[Tuple[int, List[int]]] = []
    for i, line in enumerate(lines):
        nums = [int(m.group(1).strip()) for m in CELL_RE.finditer(line)]
        if len(nums) == 3:
            candidate.append((i, nums))

    # Need 3 consecutive candidate lines (by line index)
    for idx in range(len(candidate) - 2):
        i0, r0 = candidate[idx]
        i1, r1 = candidate[idx + 1]
        i2, r2 = candidate[idx + 2]
        if i1 == i0 + 1 and i2 == i1 + 1:
            return ParsedBlock(titl=titl, rows=[r0, r1, r2], row_lines=[i0, i1, i2], skin=skin)

    raise ValueError("No 3x3 block found: expected 3 consecutive lines with 3 cells each.")


@dataclass
class EmbeddedMatrix:
    titl: Optional[str]
    anchor_line: int
    anchor_col: int
    bbox: Tuple[int, int, int, int]  # (l0,c0,l1,c1) inclusive bounds approx
    block: ParsedBlock


def scan_blocks(text: str) -> List[ParsedBlock]:
    """
    Find ALL occurrences of 3 consecutive lines with 3 numeric cell tokens.
    Overlapping matches are de-duplicated by starting line.
    """
    lines = normalize_lines(text)
    titl = detect_titl(text)
    skin = guess_skin(lines)

    candidates: List[Tuple[int, List[int]]] = []
    for i, line in enumerate(lines):
        nums = [int(m.group(1).strip()) for m in CELL_RE.finditer(line)]
        if len(nums) == 3:
            candidates.append((i, nums))

    starts = set()
    blocks: List[ParsedBlock] = []
    for idx in range(len(candidates) - 2):
        i0, r0 = candidates[idx]
        i1, r1 = candidates[idx + 1]
        i2, r2 = candidates[idx + 2]
        if i1 == i0 + 1 and i2 == i1 + 1:
            if i0 in starts:
                continue
            starts.add(i0)
            blocks.append(ParsedBlock(titl=titl, rows=[r0, r1, r2], row_lines=[i0, i1, i2], skin=skin))
    return blocks


def scan_junction(text: str) -> List[EmbeddedMatrix]:
    """
    A junction scan tries to localize each embedded block by approximating its anchor column.

    Anchor column = index of first '[' in the first row line of the block.
    Bounding box is approximate: from (row_lines[0]-1 .. row_lines[2]+1) and
    from (anchor_col-2 .. anchor_col+len(row_line)+2) clipped.
    """
    lines = normalize_lines(text)
    blocks = scan_blocks(text)
    embedded: List[EmbeddedMatrix] = []
    for b in blocks:
        l0 = b.row_lines[0]
        row_text = lines[l0]
        m = re.search(r"\[", row_text)
        anchor_col = m.start() if m else 0
        # Approximate bbox in text space
        bb_l0 = max(0, l0 - 2)
        bb_l1 = min(len(lines) - 1, b.row_lines[2] + 2)
        # Width: use longest line in that range
        width = max((len(lines[i]) for i in range(bb_l0, bb_l1 + 1)), default=len(row_text))
        bb_c0 = max(0, anchor_col - 4)
        bb_c1 = min(width, anchor_col + width)
        embedded.append(
            EmbeddedMatrix(
                titl=b.titl,
                anchor_line=l0,
                anchor_col=anchor_col,
                bbox=(bb_l0, bb_c0, bb_l1, bb_c1),
                block=b,
            )
        )
    return embedded


def gutter_overlay(text: str, start_line: int = 0) -> str:
    lines = normalize_lines(text)
    maxlen = max((len(l) for l in lines), default=0)

    # Horizontal gutter: 3 rows (hundreds / tens / ones) for readability on wide canvases
    # Example:
    #      000000000011111111112222...
    #      012345678901234567890123...
    #      0         1         2
    # We'll print:
    #   H2: (hundreds)
    #   H1: (tens)
    #   H0: (ones)
    ones = "".join(str(i % 10) for i in range(maxlen))
    tens = "".join(str((i // 10) % 10) if i % 10 == 0 else " " for i in range(maxlen))
    hund = "".join(str((i // 100) % 10) if i % 100 == 0 else " " for i in range(maxlen))

    out = []
    out.append(f"     C:{hund}")
    out.append(f"     C:{tens}")
    out.append(f"     C:{ones}")
    for idx, line in enumerate(lines):
        out.append(f"L{start_line+idx:04d} {line}")
    return "\n".join(out) + "\n"


def cmd_gutter(args: argparse.Namespace) -> int:
    path = Path(args.path)
    text = read_text(path)
    print(gutter_overlay(text))
    return 0


def cmd_addr(args: argparse.Namespace) -> int:
    if args.slot is not None:
        r, c = slot_to_rc(args.slot)
        print(json.dumps({"slot": args.slot, "row": r, "col": c}, indent=2))
        return 0
    if args.row is not None and args.col is not None:
        slot = rc_to_slot(args.row, args.col)
        print(json.dumps({"row": args.row, "col": args.col, "slot": slot}, indent=2))
        return 0
    raise SystemExit("addr requires either --slot or --row and --col")


def cmd_parse(args: argparse.Namespace) -> int:
    path = Path(args.path)
    text = read_text(path)
    block = parse_first_block(text)
    print(json.dumps(asdict(block), indent=2))
    return 0


def cmd_scan(args: argparse.Namespace) -> int:
    path = Path(args.path)
    text = read_text(path)
    embedded = scan_junction(text)
    print(json.dumps([{
        "titl": e.titl,
        "anchor_line": e.anchor_line,
        "anchor_col": e.anchor_col,
        "bbox": e.bbox,
        "rows": e.block.rows,
        "row_lines": e.block.row_lines,
        "skin": e.block.skin,
    } for e in embedded], indent=2))
    return 0


def cmd_index(args: argparse.Namespace) -> int:
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
        except Exception:
            continue
        # quick filter
        if "[" not in text or "]" not in text:
            continue
        try:
            blocks = scan_junction(text)
        except Exception:
            continue
        if not blocks:
            continue
        records.append({
            "path": str(p.relative_to(root)),
            "embedded": [{
                "titl": b.titl,
                "anchor_line": b.anchor_line,
                "anchor_col": b.anchor_col,
                "bbox": b.bbox,
                "rows": b.block.rows,
                "row_lines": b.block.row_lines,
                "skin": b.block.skin,
            } for b in blocks]
        })

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({"root": str(root), "records": records}, indent=2), encoding="utf-8")
    print(f"Wrote index: {out_path} ({len(records)} files)")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="trix", description="TRIX geometry-first helper tools")
    sub = p.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("gutter", help="print a file with line/column gutters for pinpoint references")
    g.add_argument("path")
    g.set_defaults(func=cmd_gutter)

    a = sub.add_parser("addr", help="convert between slot and row/col for a 3x3 block")
    a.add_argument("--slot", type=int)
    a.add_argument("--row", type=int)
    a.add_argument("--col", type=int)
    a.set_defaults(func=cmd_addr)

    pr = sub.add_parser("parse", help="parse the first 3x3 block in a file")
    pr.add_argument("path")
    pr.set_defaults(func=cmd_parse)

    sc = sub.add_parser("scan", help="scan a file (junction canvas) for embedded 3x3 blocks")
    sc.add_argument("path")
    sc.set_defaults(func=cmd_scan)

    ix = sub.add_parser("index", help="scan a repo tree for embedded blocks and write a JSON index")
    ix.add_argument("root")
    ix.add_argument("--out", default=".trix/index.json")
    ix.set_defaults(func=cmd_index)

    return p


def main() -> int:
    p = build_parser()
    args = p.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
