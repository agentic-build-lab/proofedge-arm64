from __future__ import annotations

import io
import json

import pytest

from proofedge.engines import LlamaCppClient


class _Response(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *_args):
        self.close()


def test_rejects_non_loopback_endpoint() -> None:
    with pytest.raises(ValueError, match="loopback"):
        LlamaCppClient("https://example.com")


def test_parses_structured_local_response(monkeypatch: pytest.MonkeyPatch) -> None:
    document = {
        "tests": [
            {
                "name": "Boundary",
                "purpose": "Compare empty input",
                "repository": "source",
                "path": "api.py",
                "line": 1,
                "inputs": [""],
                "expected_relation": "equal",
                "priority": "high",
            }
        ],
        "limitations": [],
    }
    envelope = {
        "choices": [{"message": {"content": json.dumps(document)}}],
        "timings": {"predicted_per_second": 12.5},
        "usage": {"total_tokens": 42},
    }

    def fake_urlopen(_request, timeout):
        assert timeout == 120.0
        return _Response(json.dumps(envelope).encode())

    monkeypatch.setattr("proofedge.engines.urlopen", fake_urlopen)
    response = LlamaCppClient("http://127.0.0.1:8080").generate_plan("evidence")
    assert response.document == document
    assert response.timings["predicted_per_second"] == 12.5
