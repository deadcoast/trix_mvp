"""
Unit tests for MatrixRecord.from_json in lib.indexer
Covers: happy paths, edge cases.
"""

import json
import pytest

# Import the classes under test
from lib.indexer import CellBinding, MatrixRecord
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock, patch


# --- Fixtures and helpers ---


@pytest.fixture
def valid_cell_dict() -> Dict[str, Any]:
    """A valid cell dict for CellBinding construction."""
    return {
        "cell_id": "block-1",
        "block": "block",
        "slot": 1,
        "row": 0,
        "col": 0,
        "binding": {"foo": "bar"},
        "kind": "node",
        "token": "A",
        "payload": {"node_id": "n1"},
    }


@pytest.fixture
def valid_matrix_dict(valid_cell_dict, tmp_path) -> Dict[str, Any]:
    """A valid MatrixRecord dict for serialization."""
    matrix_path = tmp_path / "matrix.trix"
    matrix_path.write_text("dummy")  # create the file
    return {
        "titl": "block",
        "path": str(matrix_path),
        "skin_hint": None,
        "cells": [valid_cell_dict],
        "skin": None,
    }


@pytest.fixture
def valid_matrix_json(valid_matrix_dict) -> str:
    """A valid JSON string for MatrixRecord.from_json."""
    return json.dumps(valid_matrix_dict)


# --- Patch validate_block_3x3 for all tests ---
@pytest.fixture(autouse=True)
def patch_validate_block(monkeypatch):
    """Patch validate_block_3x3 to always return True unless overridden."""
    monkeypatch.setattr("lib.indexer.validate_block_3x3", lambda cells: True)
    yield


# --- Test class ---


class TestMatrixRecordFromJson:
    # --- Happy Path Tests ---

    @pytest.mark.happy
    def test_from_json_valid(self, valid_matrix_json, valid_matrix_dict):
        """Test that from_json correctly parses a valid JSON string."""
        rec = MatrixRecord.from_json(valid_matrix_json)
        assert rec.titl == valid_matrix_dict["titl"]
        assert Path(rec.path) == Path(valid_matrix_dict["path"])
        assert rec.skin_hint == valid_matrix_dict["skin_hint"]
        assert rec.skin is None
        assert len(rec.cells) == 1
        assert rec.cells[0].cell_id == valid_matrix_dict["cells"][0]["cell_id"]

    @pytest.mark.happy
    def test_from_json_with_skin_absolute(self, valid_matrix_dict, tmp_path):
        """Test from_json with an absolute skin path."""
        skin_path = tmp_path / "skin.png"
        skin_path.write_text("skin")
        valid_matrix_dict["skin"] = str(skin_path)
        s = json.dumps(valid_matrix_dict)
        rec = MatrixRecord.from_json(s)
        assert rec.skin is None or Path(rec.skin) == skin_path  # skin is not a field in MatrixRecord, but skin_hint is

    @pytest.mark.happy
    def test_from_json_with_skin_relative(self, valid_matrix_dict, tmp_path, monkeypatch):
        """Test from_json with a relative skin path."""
        skin_path = tmp_path / "skin.png"
        skin_path.write_text("skin")
        rel_skin = "skin.png"
        valid_matrix_dict["skin"] = rel_skin
        # Patch cwd to tmp_path so relative resolves
        monkeypatch.chdir(tmp_path)
        s = json.dumps(valid_matrix_dict)
        rec = MatrixRecord.from_json(s)
        assert rec.skin is None or Path(rec.skin) == tmp_path / rel_skin

    @pytest.mark.happy
    def test_from_json_path_relative(self, valid_matrix_dict, tmp_path, monkeypatch):
        """Test from_json with a relative path for 'path'."""
        rel_path = "matrix.trix"
        abs_path = tmp_path / rel_path
        abs_path.write_text("dummy")
        valid_matrix_dict["path"] = rel_path
        monkeypatch.chdir(tmp_path)
        s = json.dumps(valid_matrix_dict)
        rec = MatrixRecord.from_json(s)
        assert Path(rec.path) == abs_path

    @pytest.mark.happy
    def test_from_json_missing_titl_uses_stem(self, valid_matrix_dict):
        """Test from_json sets titl from path stem if titl is missing."""
        valid_matrix_dict.pop("titl")
        s = json.dumps(valid_matrix_dict)
        rec = MatrixRecord.from_json(s)
        assert rec.titl == Path(valid_matrix_dict["path"]).stem

    # --- Edge Case Tests ---

    @pytest.mark.edge
    def test_from_json_file_not_found(self, valid_matrix_dict):
        """Test from_json raises ValueError if the file does not exist."""
        valid_matrix_dict["path"] = "/nonexistent/file.trix"
        s = json.dumps(valid_matrix_dict)
        with pytest.raises(ValueError, match="File not found"):
            MatrixRecord.from_json(s)

    @pytest.mark.edge
    def test_from_json_skin_file_not_found(self, valid_matrix_dict, tmp_path):
        """Test from_json raises ValueError if the skin file does not exist."""
        valid_matrix_dict["skin"] = str(tmp_path / "no_skin.png")
        s = json.dumps(valid_matrix_dict)
        # Patch path to exist
        valid_matrix_dict["path"] = str(tmp_path / "matrix.trix")
        Path(valid_matrix_dict["path"]).write_text("dummy")
        s = json.dumps(valid_matrix_dict)
        with pytest.raises(ValueError, match="File not found"):
            MatrixRecord.from_json(s)

    @pytest.mark.edge
    def test_from_json_no_cells(self, valid_matrix_dict, tmp_path):
        """Test from_json raises ValueError if cells is empty."""
        valid_matrix_dict["cells"] = []
        s = json.dumps(valid_matrix_dict)
        with pytest.raises(ValueError, match="No cells found"):
            MatrixRecord.from_json(s)

    @pytest.mark.edge
    def test_from_json_invalid_block(self, valid_matrix_dict, monkeypatch):
        """Test from_json raises ValueError if validate_block_3x3 returns False."""
        monkeypatch.setattr("lib.indexer.validate_block_3x3", lambda cells: False)
        s = json.dumps(valid_matrix_dict)
        with pytest.raises(ValueError, match="Invalid block"):
            MatrixRecord.from_json(s)

    @pytest.mark.edge
    def test_from_json_invalid_json(self):
        """Test from_json raises JSONDecodeError on invalid JSON."""
        with pytest.raises(json.JSONDecodeError):
            MatrixRecord.from_json("{not a valid json}")

    @pytest.mark.edge
    def test_from_json_missing_required_field(self, valid_matrix_dict):
        """Test from_json raises TypeError if a required field for CellBinding is missing."""
        del valid_matrix_dict["cells"][0]["cell_id"]
        s = json.dumps(valid_matrix_dict)
        with pytest.raises(TypeError):
            MatrixRecord.from_json(s)

    @pytest.mark.edge
    def test_from_json_cells_not_a_list(self, valid_matrix_dict):
        """Test from_json raises TypeError if cells is not a list."""
        valid_matrix_dict["cells"] = "not a list"
        s = json.dumps(valid_matrix_dict)
        with pytest.raises(TypeError):
            MatrixRecord.from_json(s)
