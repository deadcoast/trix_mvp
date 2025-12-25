from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple


BRACKET_RE = re.compile(r"\[([^\]]+)\]")


@dataclass
class TrixMatrix:
    """Canonical AST for a TRIX matrix.

    This preserves *geometry* (cells + coordinates) independent of any visual skin.

    Attributes:
        titl: 4-letter matrix title (from the ==[TITL]=== header)
        raw_cells: extracted bracket tokens for the 3x3 base block
        skin_hint: optional hint from comments (e.g. '# skin: prth')
        path: source file path
    """

    titl: str
    raw_cells: List[List[str]]
    skin_hint: Optional[str]
    path: Path

    def slots_3x3(self) -> List[Tuple[int, int, int, str]]:
        """Return (slot, row, col, token) for a 3x3 block."""
        out: List[Tuple[int, int, int, str]] = []
        slot = 1
        for r, row in enumerate(self.raw_cells):
            for c, tok in enumerate(row):
                out.append((slot, r, c, tok))
                slot += 1
        return out


def _extract_title(lines: List[str]) -> Optional[str]:
    """Find the matrix title in header lines.

    Supports skins like:
        ==[TASK]=======
        | ==[DOCS]======= |
        = ==[temp]=== =

    Strategy:
        - find a line containing '==' and at least one [token]
        - take the first bracket token on that line
        - require token length == 4 (titl spec)
    """
    for line in lines:
        if "==" not in line:
            continue
        m = BRACKET_RE.search(line)
        if not m:
            continue
        candidate = m.group(1).strip()
        if len(candidate) == 4:
            return candidate
    return None


def _extract_cell_rows(lines: List[str], title: str) -> List[List[str]]:
    """Extract 3 rows of 3 bracket tokens from the body.

    Many skins wrap rows:
        - [prth]  '- [1] [2] [3] -'
        - [clunk] '| - [1] [2] [3] - |'

    We:
        - scan lines
        - extract bracket tokens
        - filter out the title token if it appears
        - keep lines where exactly 3 tokens remain
        - stop once we collect 3 rows
    """
    rows: List[List[str]] = []
    for line in lines:
        toks = [t.strip() for t in BRACKET_RE.findall(line)]
        toks = [t for t in toks if t != title]
        if len(toks) == 3:
            rows.append(toks)
            if len(rows) == 3:
                break
    return rows


def parse_trix(path: str | Path) -> TrixMatrix:
    p = Path(path)
    txt = p.read_text(encoding="utf-8", errors="replace")
    lines = txt.splitlines()

    titl = _extract_title(lines)
    if not titl:
        raise ValueError(f"Could not find 4-letter [titl] header in {p}")

    # Optional skin hint from comments: '# skin: prth'
    skin_hint: Optional[str] = None
    for line in lines[:20]:
        s = line.strip().lower()
        if s.startswith("#") and "skin:" in s:
            skin_hint = line.split(":", 1)[1].strip()
            break

    if rows := _extract_cell_rows(lines, titl):
        return TrixMatrix(titl=titl, raw_cells=rows, skin_hint=skin_hint, path=p)
    else:
        raise ValueError(f"Could not find any 3-token cell rows in {p}")


def validate_block_3x3(m: TrixMatrix) -> List[str]:
    """Validate the base rule: 3 rows x 3 cols."""
    errs: List[str] = []
    if len(m.raw_cells) != 3:
        errs.append(f"{m.path}: expected 3 cell rows, got {len(m.raw_cells)}")
    else:
        errs.extend(
            f"{m.path}: row {i} expected 3 cells, got {len(row)}"
            for i, row in enumerate(m.raw_cells)
            if len(row) != 3
        )
    return errs
