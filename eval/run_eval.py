"""Runs the simulation across many users/sessions and compares the agent
pipeline's click-through rate against baseline strategies (random, most-popular).
"""

import random

from agents.executor import serve_item
from agents.llm import get_client
from agents.researcher import research_user
from agents.strategist import plan_next_action
from memory.store import MemoryStore
from simulator.simulate import generate_catalog, generate_users, simulate_impression


def run_baseline(strategy, users, catalog, n_sessions):
    """Run a baseline serving strategy and return a stats dict.

    "random": serve a random catalog item each session.
    "most-popular": serve whichever item has the most observed clicks so far
    (ties broken randomly), falling back to random until any item has a click.
    """
    if strategy not in ("random", "most-popular"):
        raise ValueError(f"Unknown baseline strategy: {strategy!r}")

    item_clicks = {item["id"]: 0 for item in catalog}
    clicks = 0

    for _ in range(n_sessions):
        user = random.choice(users)

        if strategy == "random":
            item = random.choice(catalog)
        else:
            top_clicks = max(item_clicks.values())
            if top_clicks == 0:
                item = random.choice(catalog)
            else:
                leaders = [i for i in catalog if item_clicks[i["id"]] == top_clicks]
                item = random.choice(leaders)

        clicked, _dwell_time = simulate_impression(user, item)
        if clicked:
            item_clicks[item["id"]] += 1
            clicks += 1

    return {
        "strategy": strategy,
        "n_sessions": n_sessions,
        "clicks": clicks,
        "ctr": clicks / n_sessions if n_sessions else 0.0,
    }


def run_agent_pipeline(users, catalog, n_sessions):
    """Run the full researcher -> strategist -> executor pipeline and return a stats dict.

    Each session: pick a user, summarize their history so far, decide what to
    serve, serve it, simulate the outcome, and log it back to memory so later
    sessions for that user reflect what was just learned.
    """
    client = get_client()
    store = MemoryStore(db_path=":memory:")
    catalog_by_id = {str(item["id"]): item for item in catalog}

    clicks = 0
    mode_counts = {"explore": 0, "exploit": 0}
    input_tokens = 0
    output_tokens = 0

    for _ in range(n_sessions):
        user = random.choice(users)
        user_id = str(user["id"])

        history = [
            {
                "category": catalog_by_id[entry["item_id"]]["category"],
                "clicked": entry["clicked"],
                "dwell_time": entry["dwell_time"],
            }
            for entry in store.get_history(user_id)
            if entry["item_id"] in catalog_by_id
        ]

        research_usage, plan_usage, serve_usage = {}, {}, {}
        summary = research_user(user_id, history, client=client, usage_out=research_usage)
        plan = plan_next_action(summary, catalog, client=client, usage_out=plan_usage)
        served = serve_item(plan, catalog, client=client, usage_out=serve_usage)
        item = served["item"]

        for usage in (research_usage, plan_usage, serve_usage):
            input_tokens += usage.get("input_tokens", 0)
            output_tokens += usage.get("output_tokens", 0)
        mode_counts[plan["mode"]] += 1

        clicked, dwell_time = simulate_impression(user, item)
        store.log_interaction(user_id, str(item["id"]), clicked, dwell_time)
        store.update_summary(user_id, summary)

        if clicked:
            clicks += 1

    store.close()
    return {
        "strategy": "agent_pipeline",
        "n_sessions": n_sessions,
        "clicks": clicks,
        "ctr": clicks / n_sessions if n_sessions else 0.0,
        "explore_count": mode_counts["explore"],
        "exploit_count": mode_counts["exploit"],
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
    }


def print_report(results):
    """Print a verbose comparison report across baseline and agent pipeline results."""
    print("=" * 60)
    print("EVAL REPORT")
    print("=" * 60)

    for result in results:
        print(f"\nStrategy: {result['strategy']}")
        print(f"  Sessions: {result['n_sessions']}")
        print(f"  Clicks:   {result['clicks']}")
        print(f"  CTR:      {result['ctr']:.2%}")
        if "explore_count" in result:
            print(f"  Mode split: explore={result['explore_count']} exploit={result['exploit_count']}")
            print(f"  Token usage: {result['input_tokens']} in / {result['output_tokens']} out")

    baseline_results = [r for r in results if r["strategy"] != "agent_pipeline"]
    agent_result = next((r for r in results if r["strategy"] == "agent_pipeline"), None)
    if agent_result and baseline_results:
        print("\n" + "-" * 60)
        print("Agent pipeline lift over baselines:")
        for baseline in baseline_results:
            if baseline["ctr"] > 0:
                lift = (agent_result["ctr"] - baseline["ctr"]) / baseline["ctr"]
                print(f"  vs {baseline['strategy']}: {lift:+.1%}")
            else:
                print(f"  vs {baseline['strategy']}: n/a (baseline had 0 clicks)")

    print("=" * 60)


if __name__ == "__main__":
    _users = generate_users(5)
    _catalog = generate_catalog(20)
    _n_sessions = 5

    _results = [
        run_baseline("random", _users, _catalog, _n_sessions),
        run_baseline("most-popular", _users, _catalog, _n_sessions),
        run_agent_pipeline(_users, _catalog, _n_sessions),
    ]

    print_report(_results)
