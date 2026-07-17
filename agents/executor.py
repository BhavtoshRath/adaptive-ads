"""Executor agent: carries out the strategist's plan and serves an actual item."""

import json
import random

from agents.llm import get_client, structured_call

# Cap on how many candidate items go in the prompt, so the catalog size
# (e.g. 1000 items) never blows up the request regardless of category size.
_MAX_CANDIDATES = 15

_SERVE_SCHEMA = {
    "type": "object",
    "properties": {
        "item_id": {"type": "integer"},
        "reason": {"type": "string"},
    },
    "required": ["item_id", "reason"],
    "additionalProperties": False,
}


def serve_item(plan, catalog, client=None, usage_out=None):
    """
    Given a serving plan from the strategist agent, pick and serve a concrete item.

    Args:
        plan: dict from plan_next_action()
        catalog: available items/ads to choose from
        client: an Anthropic client (or test double); defaults to a real one
        usage_out: optional dict; if given, populated with input_tokens/output_tokens

    Returns:
        dict with the served item and the logged reason for the decision
    """
    candidates = [item for item in catalog if item["category"] == plan["target_category"]]
    if not candidates:
        candidates = catalog

    shortlist = random.sample(candidates, min(_MAX_CANDIDATES, len(candidates)))

    client = client or get_client()
    result = structured_call(
        client,
        system=(
            "You are an ad executor. Given a serving plan and a shortlist of candidate "
            "items, pick exactly one item_id from the shortlist to serve and give a "
            "short reason tied to the plan."
        ),
        user_content=(
            f"Plan: {json.dumps(plan)}\n"
            f"Shortlist: {json.dumps([{'id': item['id'], 'category': item['category']} for item in shortlist])}\n\n"
            "Pick one item_id from the shortlist."
        ),
        schema=_SERVE_SCHEMA,
        usage_out=usage_out,
    )

    shortlist_by_id = {item["id"]: item for item in shortlist}
    chosen = shortlist_by_id.get(result["item_id"], shortlist[0])

    return {"item": chosen, "reason": result["reason"]}


if __name__ == "__main__":
    _plan = {
        "target_category": "electronics",
        "mode": "exploit",
        "reason": "User has strong preference signal for electronics.",
    }
    _catalog = [
        {"id": 1, "category": "electronics"},
        {"id": 2, "category": "sports"},
        {"id": 3, "category": "electronics"},
        {"id": 4, "category": "home"},
    ]
    _usage = {}
    print(serve_item(_plan, _catalog, usage_out=_usage))
    print("Token usage:", _usage)
