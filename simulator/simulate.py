"""Generates a synthetic user population and item catalog

Each user has a hidden preference vector across categories. Each item has a
feature vector. Simulated impressions produce a click (yes/no) and dwell time
based on how well the item matches the user's hidden preferences, plus noise.
"""

import json
import random
from pathlib import Path

CATEGORIES = ["sports", "tech", "fashion", "home", "travel"]
N_CATEGORIES = len(CATEGORIES)

# Dirichlet concentration for user preferences: <1 skews mass onto one or two
# categories, mirroring how real users tend to have a couple of strong
# interests rather than mild interest in everything.
PREFERENCE_CONCENTRATION = 0.3

# Item feature vectors: a high value in one "primary" category plus low-level
# noise elsewhere, mirroring how a real item/ad usually belongs mainly to one
# category rather than being spread evenly across all of them.
PRIMARY_FEATURE_RANGE = (0.6, 0.9)
SECONDARY_FEATURE_RANGE = (0.0, 0.15)


def generate_users(n):
    """Create n synthetic users, each with a hidden preference vector.
    preference vector: how much that user likes each of the N_CATEGORIES categories,
    drawn from a Dirichlet distribution so preferences sum to 1 and are concentrated
    in a couple of categories rather than spread uniformly."""
    users = []
    for i in range(n):
        weights = [random.gammavariate(PREFERENCE_CONCENTRATION, 1.0) for _ in range(N_CATEGORIES)]
        total = sum(weights)
        preferences = [w / total for w in weights]
        users.append({"id": i, "preferences": preferences})
    return users


def generate_catalog(m):
    """Create m synthetic items/ads, each with a feature vector.
    feature vector: how much that item belongs to / expresses each of the N_CATEGORIES
    categories. Each item is assigned one primary category with a high feature value;
    the rest of the vector is low-magnitude noise."""
    items = []
    for i in range(m):
        primary = random.randrange(N_CATEGORIES)
        features = [random.uniform(*SECONDARY_FEATURE_RANGE) for _ in range(N_CATEGORIES)]
        features[primary] = random.uniform(*PRIMARY_FEATURE_RANGE)
        items.append({"id": i, "category": CATEGORIES[primary], "features": features})
    return items


def simulate_impression(user, item):
    """Simulate a single impression: return (clicked: bool, dwell_time: float)."""
    match = sum(p * f for p, f in zip(user["preferences"], item["features"]))
    clicked = random.random() < max(0.0, min(1.0, match + random.gauss(0, 0.1)))
    dwell_time = max(0.0, match * 30 + random.gauss(0, 5)) if clicked else 0.0
    return clicked, dwell_time


def save_dataset(users, catalog, out_dir="data"):
    """Write generated users and catalog to <out_dir>/users.json and catalog.json."""
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    (out_path / "users.json").write_text(json.dumps(users, indent=2))
    (out_path / "catalog.json").write_text(json.dumps(catalog, indent=2))
    return out_path / "users.json", out_path / "catalog.json"


if __name__ == "__main__":
    generated_users = generate_users(100)
    generated_catalog = generate_catalog(1000)
    users_path, catalog_path = save_dataset(generated_users, generated_catalog)
    print(f"Wrote {len(generated_users)} users to {users_path}")
    print(f"Wrote {len(generated_catalog)} items to {catalog_path}")
