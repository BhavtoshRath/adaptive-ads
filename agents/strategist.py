"""Strategist agent: decides the serving policy for the next impression."""

import json

from agents.llm import get_client, structured_call

_PLAN_SCHEMA = {
    "type": "object",
    "properties": {
        "target_category": {"type": "string"},
        "mode": {"type": "string", "enum": ["explore", "exploit"]},
        "reason": {"type": "string"},
    },
    "required": ["target_category", "mode", "reason"],
    "additionalProperties": False,
}


def plan_next_action(user_summary, catalog, client=None, usage_out=None):
    """
    Given a user summary from the researcher agent, decide what to serve next.

    Args:
        user_summary: dict from research_user()
        catalog: available items/ads to choose from
        client: an Anthropic client (or test double); defaults to a real one
        usage_out: optional dict; if given, populated with input_tokens/output_tokens

    Returns:
        dict with target_category, mode ("explore" or "exploit"), and reason
    """
    available_categories = sorted({item["category"] for item in catalog})

    client = client or get_client()
    result = structured_call(
        client,
        system=(
            "You are an ad-serving strategist. Given a summary of a user's inferred "
            "preferences and the categories available in the catalog, decide which "
            "category to serve next. Choose 'exploit' (serve the user's known top "
            "category) when confidence is reasonably high, or 'explore' (serve a "
            "different category to gather more signal) when confidence is low or "
            "there's little history. target_category must be one of the available "
            "categories."
        ),
        user_content=(
            f"User summary: {json.dumps(user_summary)}\n"
            f"Available categories: {json.dumps(available_categories)}\n\n"
            "Decide the target category, whether this is explore or exploit, and why."
        ),
        schema=_PLAN_SCHEMA,
        usage_out=usage_out,
    )

    if result["target_category"] not in available_categories:
        result["target_category"] = available_categories[0]

    return result


if __name__ == "__main__":
    _user_summary = {
        "top_category": "electronics",
        "confidence": 0.45,
        "impression_count": 12,
    }
    _catalog = [
        {"id": "1", "category": "electronics"},
        {"id": "2", "category": "sports"},
        {"id": "3", "category": "home"},
    ]
    _usage = {}
    print(plan_next_action(_user_summary, _catalog, usage_out=_usage))
    print("Token usage:", _usage)
