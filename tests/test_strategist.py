"""Tests for agents/strategist.py's plan_next_action()."""

from agents.strategist import plan_next_action
from tests.conftest import FakeClient

_CATALOG = [
    {"id": 1, "category": "tech", "features": [0.8, 0.1, 0.1]},
    {"id": 2, "category": "sports", "features": [0.1, 0.8, 0.1]},
]


def test_plan_uses_claudes_decision_when_category_is_valid():
    client = FakeClient({"target_category": "sports", "mode": "explore", "reason": "Low confidence, try sports."})
    plan = plan_next_action({"top_category": "tech", "confidence": 0.2}, _CATALOG, client=client)
    assert plan == {"target_category": "sports", "mode": "explore", "reason": "Low confidence, try sports."}


def test_plan_falls_back_to_a_real_category_when_claude_hallucinates_one():
    client = FakeClient({"target_category": "fashion", "mode": "exploit", "reason": "hallucinated category"})
    plan = plan_next_action({"top_category": "tech", "confidence": 0.9}, _CATALOG, client=client)
    # available_categories is sorted(["tech", "sports"]) == ["sports", "tech"]
    assert plan["target_category"] == "sports"


def test_available_categories_sent_to_claude_are_deduped():
    catalog = [
        {"id": 1, "category": "tech", "features": []},
        {"id": 2, "category": "tech", "features": []},
        {"id": 3, "category": "sports", "features": []},
    ]
    client = FakeClient({"target_category": "tech", "mode": "exploit", "reason": "ok"})
    plan_next_action({"top_category": "tech", "confidence": 0.9}, catalog, client=client)
    sent_content = client.last_kwargs["messages"][0]["content"]
    assert '["sports", "tech"]' in sent_content