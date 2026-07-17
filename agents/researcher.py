"""Researcher agent: summarizes what's known about a user from their interaction history.

Per-category engagement stats are computed deterministically; Claude interprets
those stats to judge the user's top category and how confident that judgment is.
"""

import json
from collections import defaultdict

from agents.llm import get_client, structured_call

_SUMMARY_SCHEMA = {
    "type": "object",
    "properties": {
        "top_category": {"type": ["string", "null"]},
        "confidence": {"type": "number"},
        "reasoning": {"type": "string"},
    },
    "required": ["top_category", "confidence", "reasoning"],
    "additionalProperties": False,
}


def research_user(user_id, history, client=None, usage_out=None):
    """
    Given a user's interaction history, produce a summary of known preferences.

    Args:
        user_id: unique identifier for the user
        history: list of past interactions, each a dict with at least
            "category", "clicked", and "dwell_time" keys (e.g. MemoryStore
            history entries joined against the item catalog for category)
        client: an Anthropic client (or test double); defaults to a real one
        usage_out: optional dict; if given, populated with input_tokens/output_tokens

    Returns:
        dict with:
            user_id: the user_id passed in
            preferences: {category: {click_through_rate, avg_dwell_time, impressions}}
            top_category: Claude's judgment of the user's preferred category, or None
            confidence: 0.0-1.0, Claude's confidence in that judgment
            reasoning: short explanation from Claude
            n_interactions: total number of interactions considered
    """
    if not history:
        return {
            "user_id": user_id,
            "preferences": {},
            "top_category": None,
            "confidence": 0.0,
            "reasoning": "No interaction history available.",
            "n_interactions": 0,
        }

    category_stats = defaultdict(lambda: {"impressions": 0, "clicks": 0, "dwell_total": 0.0})
    for interaction in history:
        stats = category_stats[interaction["category"]]
        stats["impressions"] += 1
        if interaction["clicked"]:
            stats["clicks"] += 1
            stats["dwell_total"] += interaction["dwell_time"]

    preferences = {
        category: {
            "click_through_rate": stats["clicks"] / stats["impressions"],
            "avg_dwell_time": stats["dwell_total"] / stats["clicks"] if stats["clicks"] else 0.0,
            "impressions": stats["impressions"],
        }
        for category, stats in category_stats.items()
    }

    client = client or get_client()
    result = structured_call(
        client,
        system=(
            "You interpret a user's per-category ad engagement stats and judge which "
            "category they prefer and how confident that judgment is. Prefer categories "
            "with both a high click-through rate and enough impressions to be reliable; "
            "a high CTR on 1 impression is weaker evidence than a solid CTR on 20."
        ),
        user_content=(
            f"Per-category stats for user {user_id}:\n"
            f"{json.dumps(preferences)}\n\n"
            "Pick the category this user most prefers (or null if the data is too thin "
            "to tell), a confidence from 0.0 to 1.0, and a one-sentence reason."
        ),
        schema=_SUMMARY_SCHEMA,
        usage_out=usage_out,
    )

    return {
        "user_id": user_id,
        "preferences": preferences,
        "top_category": result["top_category"],
        "confidence": result["confidence"],
        "reasoning": result["reasoning"],
        "n_interactions": len(history),
    }


if __name__ == "__main__":
    _history = [
        {"category": "electronics", "clicked": True, "dwell_time": 12.0},
        {"category": "electronics", "clicked": True, "dwell_time": 8.5},
        {"category": "electronics", "clicked": False, "dwell_time": 0.0},
        {"category": "sports", "clicked": False, "dwell_time": 0.0},
        {"category": "home", "clicked": True, "dwell_time": 3.0},
    ]
    _usage = {}
    print(research_user("user-1", _history, usage_out=_usage))
    print("Token usage:", _usage)
