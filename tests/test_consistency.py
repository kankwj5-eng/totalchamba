"""La publicación no confunde fallos externos con cero ofertas auténticas."""
import json
from pathlib import Path
import pytest
from agent.consistency import validate_index


def write(tmp_path, jobs, status):
    path = tmp_path / "jobs.json"
    path.write_text(json.dumps({"jobs": jobs, "sources": [], "metadata": {"collection_status": status}}))
    return path


def test_empty_after_all_sources_fail_is_blocked(tmp_path):
    with pytest.raises(ValueError, match="Ninguna integración"):
        validate_index(write(tmp_path, [], {"encuentra24": "no_disponible"}))


def test_legitimate_empty_success_is_allowed(tmp_path):
    assert validate_index(write(tmp_path, [], {"lever": "sin_resultados"}))["indexed"] == 0


def test_duplicate_and_unverified_are_blocked(tmp_path):
    row = {"id": "a", "url": "https://example.org/j/2", "title": "Cajero",
           "source": "empresa", "employer_verified": True}
    with pytest.raises(ValueError, match="evidencia"):
        validate_index(write(tmp_path, [row, row], {"empresa": "actualizada"}))


def test_valid_record_is_accepted(tmp_path):
    row = {"id": "a", "url": "https://example.org/j/2", "title": "Cajero",
           "source": "empresa", "employer_verified": False}
    assert validate_index(write(tmp_path, [row], {"empresa": "actualizada"})) == {
        "indexed": 1, "sources": 0, "updated": 1}
