"""Shared Claude client and structured-output helper for the researcher/strategist/executor agents."""

import json

import anthropic
from dotenv import load_dotenv

MODEL_ID = "claude-haiku-4-5"


def get_client():
    """Build a default reusable Anthropic client, resolving credentials from the environment."""
    load_dotenv() # stores ANTHROPIC_API_KEY
    return anthropic.Anthropic()  # The client object


def structured_call(client, system, user_content, schema, max_tokens=1024): # Reusable wrapper
    """Call Claude and return its response parsed against a JSON schema."""
    response = client.messages.create(
        model=MODEL_ID,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user_content}],
        output_config={"format": {"type": "json_schema", "schema": schema}},
    )
    # Extract only the text portion from response
    text = next(block.text for block in response.content if block.type == "text")
    return json.loads(text)


if __name__ == "__main__":
    _client = get_client()
    _response = _client.messages.create(
        model=MODEL_ID,
        max_tokens=20,
        messages=[{"role": "user", "content": "Capital of the US?."}],
    )
    print(_response.content[0].text)
