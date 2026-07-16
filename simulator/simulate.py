"""Generates a synthetic user population and item catalog for the personalization demo.

Each user has a hidden preference vector across categories. Each item has a
feature vector. Simulated impressions produce a click (yes/no) and dwell time
based on how well the item matches the user's hidden preferences, plus noise.
"""


def generate_users(n):
    """Create n synthetic users, each with a hidden preference vector."""
    raise NotImplementedError


def generate_catalog(m):
    """Create m synthetic items/ads, each with a feature vector."""
    raise NotImplementedError


def simulate_impression(user, item):
    """Simulate a single impression: return (clicked: bool, dwell_time: float)."""
    raise NotImplementedError
