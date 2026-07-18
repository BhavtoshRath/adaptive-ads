"""Tests for eval/run_eval.py's run_baseline, run_agent_pipeline, and print_report."""

import pytest

from eval.run_eval import print_report, run_agent_pipeline, run_baseline
from tests.conftest import FakeClient

_USERS = [{"id": 1, "preferences": [1.0]}]
_CATALOG = [{"id": 10, "category": "tech", "features": [1.0]}]


def test_run_baseline_rejects_unknown_strategy():
    with pytest.raises(ValueError):
        run_baseline("bogus", _USERS, _CATALOG, n_sessions=1)


def test_run_baseline_random_counts_every_click(monkeypatch):
    monkeypatch.setattr("eval.run_eval.simulate_impression", lambda user, item: (True, 2.0))
    result = run_baseline("random", _USERS, _CATALOG, n_sessions=4)
    assert result == {"strategy": "random", "n_sessions": 4, "clicks": 4, "ctr": 1.0}


def test_run_baseline_most_popular_locks_onto_the_first_item_clicked(monkeypatch):
    catalog = [{"id": 1}, {"id": 2}, {"id": 3}]

    def fake_choice(seq):
        seq = list(seq)
        if len(seq) == 1:
            return seq[0]
        return next(item for item in seq if item["id"] == 2)

    def fake_simulate(user, item):
        return item["id"] == 2, 1.0 if item["id"] == 2 else 0.0

    monkeypatch.setattr("eval.run_eval.random.choice", fake_choice)
    monkeypatch.setattr("eval.run_eval.simulate_impression", fake_simulate)

    result = run_baseline("most-popular", _USERS, catalog, n_sessions=5)

    assert result == {"strategy": "most-popular", "n_sessions": 5, "clicks": 5, "ctr": 1.0}


def test_run_agent_pipeline_tracks_mode_clicks_and_token_usage(monkeypatch):
    monkeypatch.setattr("eval.run_eval.simulate_impression", lambda user, item: (True, 3.0))
    payload = {
        "top_category": "tech",
        "confidence": 0.9,
        "reasoning": "user likes tech",
        "target_category": "tech",
        "mode": "exploit",
        "reason": "known preference",
        "item_id": 10,
    }
    client = FakeClient(payload)

    result = run_agent_pipeline(_USERS, _CATALOG, n_sessions=2, client=client)

    assert result["strategy"] == "agent_pipeline"
    assert result["n_sessions"] == 2
    assert result["clicks"] == 2
    assert result["ctr"] == 1.0
    assert result["exploit_count"] == 2
    assert result["explore_count"] == 0
    # Session 1 has empty history, so research_user short-circuits without
    # calling the client; only session 2's research call adds token usage
    # on top of the 2 plan_next_action + 2 serve_item calls.
    assert result["input_tokens"] == 5 * 10
    assert result["output_tokens"] == 5 * 5


def test_print_report_shows_lift_and_handles_zero_ctr_baseline(capsys):
    results = [
        {"strategy": "random", "n_sessions": 5, "clicks": 2, "ctr": 0.4},
        {"strategy": "most-popular", "n_sessions": 5, "clicks": 0, "ctr": 0.0},
        {
            "strategy": "agent_pipeline",
            "n_sessions": 5,
            "clicks": 1,
            "ctr": 0.2,
            "explore_count": 5,
            "exploit_count": 0,
            "input_tokens": 100,
            "output_tokens": 50,
        },
    ]

    print_report(results)
    out = capsys.readouterr().out

    assert "Mode split: explore=5 exploit=0" in out
    assert "Token usage: 100 in / 50 out" in out
    assert "vs random: -50.0%" in out
    assert "vs most-popular: n/a (baseline had 0 clicks)" in out
