"""Tests for memory/store.py's SQLite-backed MemoryStore."""

import pytest

from memory.store import MemoryStore


@pytest.fixture
def store(tmp_path):
    return MemoryStore(db_path=str(tmp_path / "test_memory.db"))


def test_get_history_empty_for_unknown_user(store):
    assert store.get_history("u1") == []


def test_log_interaction_appears_in_history(store):
    store.log_interaction("u1", "item42", True, 12.5)
    history = store.get_history("u1")
    assert len(history) == 1
    entry = history[0]
    assert entry["item_id"] == "item42"
    assert entry["clicked"] is True
    assert entry["dwell_time"] == 12.5
    assert "timestamp" in entry


def test_history_is_ordered_and_scoped_per_user(store):
    store.log_interaction("u1", "item1", False, 0.0)
    store.log_interaction("u1", "item2", True, 5.0)
    store.log_interaction("u2", "item3", True, 8.0)

    u1_history = store.get_history("u1")
    assert [entry["item_id"] for entry in u1_history] == ["item1", "item2"]

    u2_history = store.get_history("u2")
    assert [entry["item_id"] for entry in u2_history] == ["item3"]


def test_get_summary_none_when_unset(store):
    assert store.get_summary("u1") is None


def test_update_summary_then_get_summary(store):
    summary = {"top_category": "tech", "confidence": 0.8}
    store.update_summary("u1", summary)
    assert store.get_summary("u1") == summary


def test_update_summary_overwrites_previous(store):
    store.update_summary("u1", {"top_category": "tech"})
    store.update_summary("u1", {"top_category": "sports"})
    assert store.get_summary("u1") == {"top_category": "sports"}