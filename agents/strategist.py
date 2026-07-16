"""Strategist agent: decides the serving policy for the next impression."""


def plan_next_action(user_summary, catalog):
    """
    Given a user summary from the researcher agent, decide what to serve next.

    Args:
        user_summary: dict from research_user()
        catalog: available items/ads to choose from

    Returns:
        dict describing the serving plan (target category, explore/exploit choice, reason)
    """
    raise NotImplementedError
