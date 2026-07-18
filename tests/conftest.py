"""Shared test fixtures: a fake Anthropic client for testing agents without network calls."""

import json


class FakeMessage:
    def __init__(self, payload, usage=None):
        self.content = [_FakeTextBlock(json.dumps(payload))]
        self.usage = usage or _FakeUsage()


class _FakeTextBlock:
    def __init__(self, text):
        self.type = "text"
        self.text = text


class _FakeUsage:
    def __init__(self, input_tokens=10, output_tokens=5):
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens


class FakeClient:
    """Stands in for anthropic.Anthropic(): .messages.create() returns a canned JSON payload."""

    def __init__(self, payload, usage=None):
        self._payload = payload
        self._usage = usage
        self.messages = self
        self.last_kwargs = None

    def create(self, **kwargs):
        self.last_kwargs = kwargs
        return FakeMessage(self._payload, usage=self._usage)
