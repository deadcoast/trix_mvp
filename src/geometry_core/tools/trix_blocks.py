#!/usr/bin/env python3
"""Block parsing and junction scanning helpers."""

from __future__ import annotations

import re

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from trix_gutters import normalize_lines


CELL_RE = re.compile(r"\[(\s*[1-9]\s*)\]")
TITL_RE = re.compile(r"\[([A-Za-z0-9]{4})\]")  # strict 4-char title token


def slot_to_rc(slot: int) -> Tuple[int, int]:
    """Convert a 1..9 slot to (row, col) in a 3x3 block."""
    if slot < 1 or slot > 9:
        raise ValueError("slot must be 1..9")
    r = (slot - 1) // 3 + 1
    c = (slot - 1) % 3 + 1
    return r, c


def rc_to_slot(r: int, c: int) -> int:
    """Convert a 1..3 row/col to a slot in a 3x3 block."""
    if r < 1 or r > 3 or c < 1 or c > 3:
        raise ValueError("row/col must be 1..3 for a 3x3 block")
    return (r - 1) * 3 + c


def guess_skin_from_lines(lines: List[str]) -> Optional[str]:
    """Heuristically infer an ASCII skin from nearby header/row patterns."""
    joined = "\n".join(lines[:8])
    if "| ==[" in joined and "| - [" in joined:
        return "clunk"
    if "= ==[" in joined and "| [1]" in joined:
        return "fcy"
    if re.search(r"^==\[[A-Za-z0-9]{4}\]", joined, flags=re.M):
        return "prth_or_boring"
    return None


def detect_titl_near(lines: List[str], line_idx: int, anchor_col: int) -> Optional[str]:
    """Detect a 4-char [titl] token near a given (line, col)."""
    for back in range(1, 6):
        li = line_idx - back
        if li < 0:
            break
        matches = list(TITL_RE.finditer(lines[li]))
        if not matches:
            continue
        best = min(matches, key=lambda m: abs(m.start() - anchor_col))
        return best.group(1)

    matches = list(TITL_RE.finditer(lines[line_idx])) if 0 <= line_idx < len(lines) else []
    if matches:
        best = min(matches, key=lambda m: abs(m.start() - anchor_col))
        return best.group(1)
    return None


@dataclass
class CellBox:
    """Text-space bounding box for a single cell token."""
    slot: int
    token: int
    line: int
    col0: int
    col1: int

    @property
    def center(self) -> Tuple[int, int]:
        """Return the (line, col) center of the token."""
        return (self.line, (self.col0 + self.col1) // 2)


@dataclass
class ParsedBlock:
    """Parsed 3x3 block with rows, coordinates, and skin hint."""
    titl: Optional[str]
    rows: List[List[int]]
    row_lines: List[int]
    cells: List[CellBox]
    skin: Optional[str] = None


@dataclass
class EmbeddedMatrix:
    """A localized 3x3 block within a junction canvas."""
    titl: Optional[str]
    anchor_line: int
    anchor_col: int
    bbox: Tuple[int, int, int, int]
    block: ParsedBlock


def parse_first_block(text: str) -> ParsedBlock:
    """Extract the first 3 consecutive lines that each contain exactly 3 numeric cells [1]..[9]."""
    lines = normalize_lines(text)
    skin = guess_skin_from_lines(lines)

    candidate: List[Tuple[int, List[Tuple[int, int, int]]]] = []
    for i, line in enumerate(lines):
        toks = [(int(m.group(1).strip()), m.start(), m.end() - 1) for m in CELL_RE.finditer(line)]
        if len(toks) == 3:
            candidate.append((i, toks))

    for idx in range(len(candidate) - 2):
        i0, t0 = candidate[idx]
        i1, t1 = candidate[idx + 1]
        i2, t2 = candidate[idx + 2]
        if i1 == i0 + 1 and i2 == i1 + 1:
            rows = [
                [t for (t, _, _) in t0],
                [t for (t, _, _) in t1],
                [t for (t, _, _) in t2],
            ]
            row_lines = [i0, i1, i2]

            anchor_col = t0[0][1]
            titl = detect_titl_near(lines, i0, anchor_col)

            cells: List[CellBox] = []
            slot = 1
            for li, row in zip(row_lines, [t0, t1, t2]):
                for tok, c0, c1 in row:
                    cells.append(CellBox(slot=slot, token=tok, line=li, col0=c0, col1=c1))
                    slot += 1

            return ParsedBlock(titl=titl, rows=rows, row_lines=row_lines, cells=cells, skin=skin)

    raise ValueError("No 3x3 block found: expected 3 consecutive lines with 3 cells each.")


def scan_blocks(text: str) -> List[ParsedBlock]:
    """Find ALL embedded 3x3 blocks in a text buffer."""
    lines = normalize_lines(text)
    skin = guess_skin_from_lines(lines)

    @dataclass(frozen=True)
    class RowCand:
        """Candidate triple of adjacent cell tokens from a single row."""
        line: int
        anchor_col: int
        toks: List[Tuple[int, int, int]]

    max_within_gap = 8

    def _row_candidates_for_line(line_text: str, line_idx: int) -> List[RowCand]:
        toks = [
            (int(m.group(1).strip()), m.start(), m.end() - 1)
            for m in CELL_RE.finditer(line_text)
        ]
        if len(toks) < 3:
            return []
        cands: List[RowCand] = []
        for i in range(len(toks) - 2):
            t0, t1, t2 = toks[i], toks[i + 1], toks[i + 2]
            gap1 = t1[1] - t0[1]
            gap2 = t2[1] - t1[1]
            t0n, t1n, t2n = t0[0], t1[0], t2[0]
            if (
                t0n in (1, 4, 7)
                and t1n == t0n + 1
                and t2n == t0n + 2
                and gap1 <= max_within_gap
                and gap2 <= max_within_gap
            ):
                cands.append(RowCand(line=line_idx, anchor_col=t0[1], toks=[t0, t1, t2]))
        if not cands:
            return []
        dedup: Dict[int, RowCand] = {}
        for cand in cands:
            dedup.setdefault(cand.anchor_col, cand)
        return list(dedup.values())

    row_cands_by_line: Dict[int, List[RowCand]] = {}

    for li, line in enumerate(lines):
        if cands := _row_candidates_for_line(line, li):
            row_cands_by_line[li] = cands

    blocks: List[ParsedBlock] = []
    seen: set[Tuple[int, int]] = set()

    for li0, cands0 in row_cands_by_line.items():
        li1, li2 = li0 + 1, li0 + 2
        if li1 not in row_cands_by_line or li2 not in row_cands_by_line:
            continue

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

            blocks.append(
                ParsedBlock(
                    titl=titl,
                    rows=[r0, r1, r2],
                    row_lines=row_lines,
                    cells=cells,
                    skin=skin,
                )
            )
            seen.add((li0, anchor))

    return blocks


def scan_junction(text: str) -> List[EmbeddedMatrix]:
    """Scan a file and localize each embedded 3x3 block."""
    lines = normalize_lines(text)
    blocks = scan_blocks(text)

    embedded: List[EmbeddedMatrix] = []
    pad = 6
    for b in blocks:
        anchor_line = b.row_lines[0]
        anchor_col = min((c.col0 for c in b.cells), default=0)

        bb_l0 = max(0, anchor_line - 2)
        bb_l1 = min(len(lines) - 1, b.row_lines[2] + 2)

        min_c = min((c.col0 for c in b.cells), default=0)
        max_c = max((c.col1 for c in b.cells), default=0)

        bb_c0 = max(0, min_c - pad)
        bb_c1 = max_c + pad

        if max_width := max((len(lines[i]) for i in range(bb_l0, bb_l1 + 1)), default=0):
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


def resolve_coordinate(text: str, line: int, col: int) -> Dict[str, Any]:
    """Resolve an absolute (line, col) to an embedded matrix + slot."""
    lines = normalize_lines(text)
    if line < 0 or line >= len(lines):
        return {
            "line": line,
            "col": col,
            "hit": None,
        }
    embedded = scan_junction(text)

    hits = []
    for e in embedded:
        for cb in e.block.cells:
            if cb.line == line and cb.col0 <= col <= cb.col1:
                hits.append((0, e, cb))
            else:
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
