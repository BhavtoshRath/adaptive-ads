"""Runs the simulation across many users/sessions and compares the agent
pipeline's click-through rate against baseline strategies (random, most-popular).
"""


def run_baseline(strategy, users, catalog, n_sessions):
    """Run a baseline serving strategy and return its click-through rate."""
    raise NotImplementedError


def run_agent_pipeline(users, catalog, n_sessions):
    """Run the full researcher -> strategist -> executor pipeline and return CTR."""
    raise NotImplementedError


if __name__ == "__main__":
    print("Eval harness not yet implemented.")
