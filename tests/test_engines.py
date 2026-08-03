from __future__ import annotations

import json

import pytest

from proofedge.engines import (
    MAX_RESPONSE_BYTES,
    LlamaCppClient,
    LlamaCppError,
    validate_plan_document,
)


class _Response:
    def __init__(self, payload: bytes) -> None:
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def read(self, _limit: int) -> bytes:
        return self.payload


@pytest.mark.parametrize(
    "endpoint",
    [
        "https://example.com",
        "http://localhost:8080/api",
        "http://localhost:8080?redirect=http://example.com",
        "http://user:password@localhost:8080",
        "http://localhost:not-a-port",
    ],
)
def test_rejects_non_loopback_or_ambiguous_endpoint(endpoint: str) -> None:
    with pytest.raises(ValueError, match="loopback"):
        LlamaCppClient(endpoint)


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

    def fake_open(_request, timeout):
        assert timeout == 120.0
        request_payload = json.loads(_request.data)
        assert request_payload["cache_prompt"] is False
        return _Response(json.dumps(envelope).encode())

    monkeypatch.setattr("proofedge.engines._LOCAL_OPENER.open", fake_open)
    response = LlamaCppClient("http://127.0.0.1:8080").generate_plan("evidence")
    assert response.document == document
    assert response.timings["predicted_per_second"] == 12.5


def test_caps_local_model_response_bytes(monkeypatch: pytest.MonkeyPatch) -> None:
    def oversized(_request, timeout):
        assert timeout == 120.0
        return _Response(b"x" * (MAX_RESPONSE_BYTES + 1))

    monkeypatch.setattr("proofedge.engines._LOCAL_OPENER.open", oversized)
    with pytest.raises(LlamaCppError, match="byte limit"):
        LlamaCppClient("http://127.0.0.1:8080").generate_plan("evidence")


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ({"line": 0}, "evidence line"),
        ({"line": -1}, "evidence line"),
        ({"line": True}, "evidence line"),
        ({"repository": "manifest"}, "repository"),
        ({"priority": "urgent"}, "priority"),
        ({"inputs": []}, "inputs array"),
        ({"unexpected": "field"}, "test object"),
    ],
)
def test_strictly_validates_plan_schema(mutation: dict, message: str) -> None:
    proposal = {
        "name": "Boundary",
        "purpose": "Compare empty input",
        "repository": "source",
        "path": "api.py",
        "line": 1,
        "inputs": [""],
        "expected_relation": "equal",
        "priority": "high",
    }
    proposal.update(mutation)
    with pytest.raises(LlamaCppError, match=message):
        validate_plan_document({"tests": [proposal], "limitations": []})


def test_rejects_empty_or_extra_plan_envelopes() -> None:
    with pytest.raises(LlamaCppError, match="tests array"):
        validate_plan_document({"tests": [], "limitations": []})
    with pytest.raises(LlamaCppError, match="plan object"):
        validate_plan_document({"tests": [], "limitations": [], "extra": True})
