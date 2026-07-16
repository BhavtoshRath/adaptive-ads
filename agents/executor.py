"""Executor agent: carries out the strategist's plan and serves an actual item."""


def serve_item(plan, catalog):
    """
    Given a serving plan from the strategist agent, pick and serve a concrete item.

    Args:
        plan: dict from plan_next_action()
        catalog: available items/ads to choose from

    Returns:
        dict with the served item and the logged reason for the decision
    """
    raise NotImplementedError
