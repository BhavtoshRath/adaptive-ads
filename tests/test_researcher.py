"""Tests for agents/researcher.py's research_user()."""

from agents.researcher import research_user
from tests.conftest import FakeClient


def _interaction(category, clicked, dwell_time=0.0):
    return {"category": category, "clicked": clicked, "dwell_time": dwell_time}


def test_empty_history_short_circuits_without_calling_claude():
    client = FakeClient({"top_category": "should-not-be-used", "confidence": 1.0, "reasoning": "n/a"})
    summary = research_user("u1", [], client=client)
    assert summary == {
        "user_id": "u1",
        "preferences": {},
        "top_category": None,
        "confidence": 0.0,
        "reasoning": "No interaction history available.",
        "n_interactions": 0,
    }
    assert client.last_kwargs is None


def test_computed_preferences_are_deterministic_regardless_of_claude():
    history = [
        _interaction("tech", True, dwell_time=5.0),
        _interaction("tech", False),
        _interaction("sports", True, dwell_time=20.0),
    ]
    client = FakeClient({"top_category": "sports", "confidence": 0.6, "reasoning": "Higher CTR on sports."})
    summary = research_user("u1", history, client=client)
    assert summary["preferences"]["tech"] == {
        "click_through_rate": 0.5,
        "avg_dwell_time": 5.0,
        "impressions": 2,
    }
    assert summary["preferences"]["sports"] == {
        "click_through_rate": 1.0,
        "avg_dwell_time": 20.0,
        "impressions": 1,
    }
    assert summary["n_interactions"] == 3


def test_claudes_judgment_is_passed_through_into_the_summary():
    history = [_interaction("tech", True, dwell_time=10.0)]
    client = FakeClient({"top_category": "tech", "confidence": 0.8, "reasoning": "Only category seen, clicked."})
    summary = research_user("u1", history, client=client)
    assert summary["top_category"] == "tech"
    assert summary["confidence"] == 0.8
    assert summary["reasoning"] == "Only category seen, clicked."
