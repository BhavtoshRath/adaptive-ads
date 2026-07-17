"""Shared test fixtures: a fake Anthropic client for testing agents without network calls."""

import json


class FakeMessage:
    def __init__(self, payload):
        self.content = [_FakeTextBlock(json.dumps(payload))]


class _FakeTextBlock:
    def __init__(self, text):
        self.type = "text"
        self.text = text


class FakeClient:
    """Stands in for anthropic.Anthropic(): .messages.create() returns a canned JSON payload."""

    def __init__(self, payload):
        self._payload = payload
        self.messages = self
        self.last_kwargs = None

    def create(self, **kwargs):
        self.last_kwargs = kwargs
        return FakeMessage(self._payload)
