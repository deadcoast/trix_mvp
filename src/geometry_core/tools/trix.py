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


def guess_skin_from_lines(lines: List[str]) -> Optional[str]:
    joined = "\n".join(lines[:8])
    if "| ==[" in joined and "| - [" in joined:
        return "clunk"
    if "= ==[" in joined and "| [1]" in joined:
        return "fcy"
    if re.search(r"^==\[[A-Za-z0-9]{4}\]", joined, flags=re.M):
        return "prth_or_boring"
    return None


def detect_titl_near(lines: List[str], line_idx: int, anchor_col: int) -> Optional[str]:
    """Detect a 4-char [titl] token near a given (line, col).

    Junction canvases may contain multiple matrices, so we do *local* title detection:
    - Look upward a few lines for TITL tokens, prefer the closest in column.
    - Fallback to searching the same line.
    """
    # search upward (header lines often sit above the 3×3 body rows)
    for back in range(1, 6):
        li = line_idx - back
        if li < 0:
            break
        matches = list(TITL_RE.finditer(lines[li]))
        if not matches:
            continue
        best = min(matches, key=lambda m: abs(m.start() - anchor_col))
        return best.group(1)

    # fallback: same line
    matches = list(TITL_RE.finditer(lines[line_idx])) if 0 <= line_idx < len(lines) else []
    if matches:
        best = min(matches, key=lambda m: abs(m.start() - anchor_col))
        return best.group(1)
    return None


@dataclass
class CellBox:
    slot: int
    token: int
    line: int
    col0: int
    col1: int

    @property
    def center(self) -> Tuple[int, int]:
        return (self.line, (self.col0 + self.col1) // 2)


@dataclass
class ParsedBlock:
    titl: Optional[str]
    rows: List[List[int]]           # 3 rows x 3 cols of numeric tokens
    row_lines: List[int]            # line indices where each row was found
    cells: List[CellBox]            # 9 CellBox entries with text-space coordinates
    skin: Optional[str] = None


def parse_first_block(text: str) -> ParsedBlock:
    """Extract the first 3 consecutive lines that each contain exactly 3 numeric cells [1]..[9]."""
    lines = normalize_lines(text)
    skin = guess_skin_from_lines(lines)

    candidate: List[Tuple[int, List[Tuple[int, int, int]]]] = []
    for i, line in enumerate(lines):
        # capture (token, col0, col1)
        toks = [(int(m.group(1).strip()), m.start(), m.end() - 1) for m in CELL_RE.finditer(line)]
        if len(toks) == 3:
            candidate.append((i, toks))

    for idx in range(len(candidate) - 2):
        i0, t0 = candidate[idx]
        i1, t1 = candidate[idx + 1]
        i2, t2 = candidate[idx + 2]
        if i1 == i0 + 1 and i2 == i1 + 1:
            rows = [[t for (t, _, _) in t0], [t for (t, _, _) in t1], [t for (t, _, _) in t2]]
            row_lines = [i0, i1, i2]

            # anchor column = first '[' in first row
            anchor_col = t0[0][1]
            titl = detect_titl_near(lines, i0, anchor_col)

            cells: List[CellBox] = []
            slot = 1
            for r_idx, (li, row) in enumerate(zip(row_lines, [t0, t1, t2])):
                for c_idx, (tok, c0, c1) in enumerate(row):
                    cells.append(CellBox(slot=slot, token=tok, line=li, col0=c0, col1=c1))
                    slot += 1

            return ParsedBlock(titl=titl, rows=rows, row_lines=row_lines, cells=cells, skin=skin)

    raise ValueError("No 3x3 block found: expected 3 consecutive lines with 3 cells each.")


@dataclass
class EmbeddedMatrix:
    titl: Optional[str]
    anchor_line: int
    anchor_col: int
    bbox: Tuple[int, int, int, int]  # (l0,c0,l1,c1) inclusive bounds approx
    block: ParsedBlock


def scan_blocks(text: str) -> List[ParsedBlock]:
    """Find ALL embedded 3×3 blocks in a text buffer.

    Junction canvases can place multiple matrices side-by-side, which means a single
    row line may contain 6, 9, 12... numeric cell tokens.

    Strategy:
    - For each line, find *all* numeric cell tokens with their (token, col0, col1).
    - Create *row candidates* by taking triples of adjacent tokens whose spacing
      indicates they belong to the same 3-cell row.
    - Stitch 3 consecutive row candidates with the same anchor_col into a block.
    """
    lines = normalize_lines(text)
    skin = guess_skin_from_lines(lines)

    @dataclass(frozen=True)
    class RowCand:
        line: int
        anchor_col: int           # col0 of first cell token in the row triple
        toks: List[Tuple[int,int,int]]  # (token, col0, col1) ×3

    # Heuristics: inside a 3×3 row, tokens are close; between matrices there's a bigger gap.
    MAX_WITHIN_GAP = 8

    row_cands_by_line: Dict[int, List[RowCand]] = {}

    for li, line in enumerate(lines):
        toks = [(int(m.group(1).strip()), m.start(), m.end() - 1) for m in CELL_RE.finditer(line)]
        if len(toks) < 3:
            continue

        cands: List[RowCand] = []
        # Sliding windows of 3 tokens
        for i in range(len(toks) - 2):
            t0, t1, t2 = toks[i], toks[i + 1], toks[i + 2]
            gap1 = t1[1] - t0[1]
            gap2 = t2[1] - t1[1]
            t0n, t1n, t2n = t0[0], t1[0], t2[0]
            if (
                t0n in (1, 4, 7)
                and t1n == t0n + 1
                and t2n == t0n + 2
                and gap1 <= MAX_WITHIN_GAP
                and gap2 <= MAX_WITHIN_GAP
            ):
                cands.append(RowCand(line=li, anchor_col=t0[1], toks=[t0, t1, t2]))
        if cands:
            # De-dup candidates by anchor_col (keep left-most triple for that anchor)
            dedup: Dict[int, RowCand] = {}
            for c in cands:
                dedup.setdefault(c.anchor_col, c)
            row_cands_by_line[li] = list(dedup.values())

    blocks: List[ParsedBlock] = []
    seen: set[Tuple[int,int]] = set()  # (start_line, anchor_col)

    for li0, cands0 in row_cands_by_line.items():
        li1, li2 = li0 + 1, li0 + 2
        if li1 not in row_cands_by_line or li2 not in row_cands_by_line:
            continue

        # Index next lines by anchor_col
        by_anchor1 = {c.anchor_col: c for c in row_cands_by_line[li1]}
        by_anchor2 = {c.anchor_col: c for c in row_cands_by_line[li2]}

        for c0 in cands0:
            anchor = c0.anchor_col
            if (li0, anchor) in seen:
                continue
            c1 = by_anchor1.get(anchor)
            c2 = by_anchor2.get(anchor)
            if not c1 or not c2:
                continue

            # Build rows (token numbers only)
            r0 = [t for (t, _, _) in c0.toks]
            r1 = [t for (t, _, _) in c1.toks]
            r2 = [t for (t, _, _) in c2.toks]

            row_lines = [li0, li1, li2]
            titl = detect_titl_near(lines, li0, anchor)

            cells: List[CellBox] = []
            slot = 1
            for li, row in zip(row_lines, [c0.toks, c1.toks, c2.toks]):
                for tok, c0x, c1x in row:
                    cells.append(CellBox(slot=slot, token=tok, line=li, col0=c0x, col1=c1x))
                    slot += 1

            blocks.append(ParsedBlock(titl=titl, rows=[r0, r1, r2], row_lines=row_lines, cells=cells, skin=skin))
            seen.add((li0, anchor))

    return blocks


def scan_junction(text: str) -> List[EmbeddedMatrix]:
    """Scan a file and localize each embedded 3×3 block.

    For each detected block we compute:
    - anchor_line: first row line (0-based)
    - anchor_col: left-most '[' of the block (0-based)
    - bbox: approximate bounding box around the block in text-space
    """
    lines = normalize_lines(text)
    blocks = scan_blocks(text)

    embedded: List[EmbeddedMatrix] = []
    for b in blocks:
        anchor_line = b.row_lines[0]
        anchor_col = min((c.col0 for c in b.cells), default=0)

        # Vertical bounds: a little padding above/below the 3 cell rows
        bb_l0 = max(0, anchor_line - 2)
        bb_l1 = min(len(lines) - 1, b.row_lines[2] + 2)

        # Horizontal bounds: bound tightly around the cell tokens
        min_c = min((c.col0 for c in b.cells), default=0)
        max_c = max((c.col1 for c in b.cells), default=0)

        pad = 6
        bb_c0 = max(0, min_c - pad)
        bb_c1 = max_c + pad

        # Clip to local line widths
        max_width = max((len(lines[i]) for i in range(bb_l0, bb_l1 + 1)), default=0)
        if max_width:
            bb_c1 = min(bb_c1, max_width - 1)

        embedded.append(
            EmbeddedMatrix(
                titl=b.titl,
                anchor_line=anchor_line,
                anchor_col=anchor_col,
                bbox=(bb_l0, bb_c0, bb_l1, bb_c1),
                block=b,
            )
        )
    return embedded


def gutter_overlay(text: str, start_line: int = 0) -> str:
    """Overlay L#### and C#### gutters on any text."""
    lines = normalize_lines(text)
    maxlen = max((len(l) for l in lines), default=0)

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


def _parse_lc(arg: str) -> Tuple[int, int]:
    """Parse 'L####:C####' (or 'L42:C137') into (line, col)."""
    m = re.match(r"L(\d+):C(\d+)", arg.strip(), flags=re.I)
    if not m:
        raise ValueError("Expected format L####:C####")
    return int(m.group(1)), int(m.group(2))


def _guttered_vlg_hlg_to_lc(lines: List[str], vlg: int, hlg: int) -> Tuple[int, int]:
    """Convert (vlg, hlg) from the native junction gutter grid into text (line, col).

    This supports the gutter style shown in src/geometry_core/matrix_junction.md:

        |17| ... |
        ...
        +--+--+--+...
        |01|02|03|...

    Mapping rules:
    - vlg: matches a row label '|NN|' at the start of a line.
    - hlg: matches the column label line '|01|02|...|', using bar positions as boundaries.
      We return the center column of the hlg cell interior.
    """
    # Find row line by label
    row_line = None
    for i, l in enumerate(lines):
        m = re.match(r"\|(\d{2})\|", l)
        if not m:
            continue
        if int(m.group(1)) == int(vlg):
            row_line = i
            break
    if row_line is None:
        raise ValueError(f"Could not find vlg row {vlg:02d} in file")

    # Find horizontal label line
    hlabel_idx = None
    for i, l in enumerate(lines):
        if re.match(r"\|01\|02\|", l):
            hlabel_idx = i
            break
    if hlabel_idx is None:
        raise ValueError("Could not find horizontal gutter line starting with '|01|02|'")

    hlabel = lines[hlabel_idx]
    bars = [m.start() for m in re.finditer(r"\|", hlabel)]
    # We expect 1..N coords, each coord cell is between bars[k-1]..bars[k]
    if hlg < 1 or hlg >= len(bars):
        raise ValueError(f"hlg must be 1..{len(bars)-1}, got {hlg}")

    x0 = bars[hlg - 1] + 1
    x1 = bars[hlg] - 1
    col = (x0 + x1) // 2
    return row_line, col


def resolve_coordinate(text: str, line: int, col: int) -> Dict[str, object]:
    """Resolve an absolute (line, col) to an embedded matrix + slot."""
    lines = normalize_lines(text)
    embedded = scan_junction(text)

    # Compute candidate token hits
    hits = []
    for e in embedded:
        for cb in e.block.cells:
            if cb.line == line and cb.col0 <= col <= cb.col1:
                hits.append((0, e, cb))  # exact hit
            else:
                # distance to center for fallback ranking
                dl = abs(cb.center[0] - line)
                dc = abs(cb.center[1] - col)
                hits.append((dl + dc + 1000, e, cb))

    if not hits:
        return {
            "line": line,
            "col": col,
            "hit": None,
        }

    hits.sort(key=lambda t: t[0])
    score, e, cb = hits[0]
    return {
        "line": line,
        "col": col,
        "hit": {
            "score": score,
            "matrix": e.titl,
            "slot": cb.slot,
            "token": cb.token,
            "token_bbox": {"line": cb.line, "col0": cb.col0, "col1": cb.col1},
            "address": f"{e.titl}#{cb.slot}" if e.titl else None,
        },
        "embedded_count": len(embedded),
    }


def extract_region_vlg_hlg(text: str, vlg0: int, vlg1: int, hlg0: int, hlg1: int) -> Dict[str, object]:
    """Extract a rectangular region from a native-gutter junction canvas (vlg/hlg).

    Returns the raw text slice for each vlg row included.
    """
    lines = normalize_lines(text)

    # Find horizontal label line and compute bar boundaries
    hlabel_idx = None
    for i, l in enumerate(lines):
        if re.match(r"\|01\|02\|", l):
            hlabel_idx = i
            break
    if hlabel_idx is None:
        raise ValueError("Could not find horizontal gutter line starting with '|01|02|'")

    hlabel = lines[hlabel_idx]
    bars = [m.start() for m in re.finditer(r"\|", hlabel)]
    if hlg0 < 1 or hlg1 < 1 or hlg0 >= len(bars) or hlg1 >= len(bars):
        raise ValueError(f"hlg must be 1..{len(bars)-1}")

    hmin, hmax = min(hlg0, hlg1), max(hlg0, hlg1)
    x0 = bars[hmin - 1] + 1
    x1 = bars[hmax] - 1

    # Map vlg rows to line indices
    v_to_line: Dict[int, int] = {}
    for i, l in enumerate(lines):
        m = re.match(r"\|(\d{2})\|", l)
        if m:
            v_to_line[int(m.group(1))] = i

    vmin, vmax = min(vlg0, vlg1), max(vlg0, vlg1)
    missing = [v for v in range(vmin, vmax + 1) if v not in v_to_line]
    if missing:
        raise ValueError(f"Missing vlg rows: {missing}")

    rows = []
    for v in range(vmax, vmin - 1, -1):  # preserve the visual top-down order
        li = v_to_line[v]
        rows.append({
            "vlg": v,
            "line": li,
            "slice": lines[li][x0:x1 + 1],
        })

    return {
        "vlg": [vmin, vmax],
        "hlg": [hmin, hmax],
        "x0": x0,
        "x1": x1,
        "rows": rows,
    }


def cmd_gutter(args: argparse.Namespace) -> int:
    path = Path(args.path)
    print(gutter_overlay(read_text(path)))
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
    block = parse_first_block(read_text(path))
    print(json.dumps(asdict(block), indent=2))
    return 0


def cmd_scan(args: argparse.Namespace) -> int:
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


def cmd_resolve(args: argparse.Namespace) -> int:
    path = Path(args.path)
    text = read_text(path)
    lines = normalize_lines(text)

    if args.lc:
        line, col = _parse_lc(args.lc)
    elif args.line is not None and args.col is not None:
        line, col = int(args.line), int(args.col)
    elif args.vlg is not None and args.hlg is not None:
        line, col = _guttered_vlg_hlg_to_lc(lines, int(args.vlg), int(args.hlg))
    else:
        raise SystemExit("resolve requires either --lc, --line/--col, or --vlg/--hlg")

    result = resolve_coordinate(text, line=line, col=col)
    print(json.dumps(result, indent=2))
    return 0


def cmd_extract(args: argparse.Namespace) -> int:
    path = Path(args.path)
    text = read_text(path)
    result = extract_region_vlg_hlg(text, args.vlg0, args.vlg1, args.hlg0, args.hlg1)
    print(json.dumps(result, indent=2))
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
        if "[" not in text or "]" not in text:
            continue
        try:
            blocks = scan_junction(text)
        except Exception:
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
    out_path.write_text(json.dumps({"root": str(root), "records": records}, indent=2), encoding="utf-8")
    print(f"Wrote index: {out_path} ({len(records)} files)")
    return 0


def build_parser() -> argparse.ArgumentParser:
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
    rs.add_argument("--vlg", type=int, help="Vertical line gutter index (native junction style, 2-digit rows)")
    rs.add_argument("--hlg", type=int, help="Horizontal line gutter index (native junction style)")
    rs.set_defaults(func=cmd_resolve)

    ex = sub.add_parser("extract", help="extract a (vlg/hlg) rectangular region from a native-gutter junction")
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
    p = build_parser()
    args = p.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
