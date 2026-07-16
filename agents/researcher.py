"""Researcher agent: summarizes what's known about a user from their interaction history."""


def research_user(user_id, history):
    """
    Given a user's interaction history, produce a summary of known preferences.

    Args:
        user_id: unique identifier for the user
        history: list of past interactions (clicks, dwell time, skips)

    Returns:
        dict summarizing inferred preferences and confidence level
    """
    raise NotImplementedError
