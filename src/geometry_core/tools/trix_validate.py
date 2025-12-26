#!/usr/bin/env python3
"""Helpers for block-labeled junction validation."""

from __future__ import annotations

import re

from typing import Dict

try:
    from .trix_gutters import normalize_lines
except ImportError:  # pragma: no cover
    from trix_gutters import normalize_lines


def _normalize_block_label(label: str) -> str:
    """Normalize a block label to a consistent token."""
    token = re.sub(r"[^a-z0-9]+", "_", label.strip().lower())
    return token.strip("_")


def _extract_labeled_blocks(text: str) -> Dict[str, str]:
    """Extract fenced code blocks that follow '> <label>' markers."""
    lines = normalize_lines(text)
    blocks: Dict[str, str] = {}
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith(">"):
            label = line[1:].strip()
            name = _normalize_block_label(label)
            j = i + 1
            while j < len(lines):
                peek = lines[j].strip()
                if peek.startswith(">"):
                    break
                if peek.startswith("```"):
                    break
                j += 1
            if j >= len(lines) or lines[j].strip().startswith(">"):
                i += 1
                continue
            start = j + 1
            k = start
            while k < len(lines) and not lines[k].strip().startswith("```"):
                k += 1
            blocks[name] = "\n".join(lines[start:k])
            i = k + 1
            continue
        i += 1
    return blocks
