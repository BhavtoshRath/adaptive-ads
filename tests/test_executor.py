"""Tests for agents/executor.py's serve_item()."""

from agents.executor import serve_item
from tests.conftest import FakeClient

_CATALOG = [
    {"id": 1, "category": "tech", "features": [0.8, 0.1]},
    {"id": 2, "category": "tech", "features": [0.7, 0.2]},
    {"id": 3, "category": "sports", "features": [0.1, 0.8]},
]


def test_serve_item_returns_claudes_chosen_item_from_shortlist():
    client = FakeClient({"item_id": 2, "reason": "Best match for tech."})
    plan = {"target_category": "tech", "mode": "exploit", "reason": "user likes tech"}
    result = serve_item(plan, _CATALOG, client=client)
    assert result["item"]["id"] == 2
    assert result["item"]["category"] == "tech"
    assert result["reason"] == "Best match for tech."


def test_serve_item_falls_back_when_claude_hallucinates_an_item_id():
    client = FakeClient({"item_id": 999, "reason": "not a real item"})
    plan = {"target_category": "tech", "mode": "exploit", "reason": "user likes tech"}
    result = serve_item(plan, _CATALOG, client=client)
    assert result["item"]["category"] == "tech"


def test_serve_item_falls_back_to_full_catalog_when_category_has_no_items():
    client = FakeClient({"item_id": 3, "reason": "only option"})
    plan = {"target_category": "fashion", "mode": "explore", "reason": "no fashion items"}
    result = serve_item(plan, _CATALOG, client=client)
    assert result["item"]["id"] == 3