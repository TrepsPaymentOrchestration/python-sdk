from __future__ import annotations

import json
import time
from collections import deque

import pytest

from treps.client import TransportResponse, TrepsClient, TrepsEnvironment
from treps.errors import TrepsApiError


def _now_ms() -> int:
    return int(time.time() * 1000)


class _FakeTransport:
    """Records each request and replays a queued response, mirroring the Node SDK's fetch-mock tests."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, str, dict[str, str], bytes | None]] = []
        self._responses: deque[TransportResponse] = deque()

    def enqueue(self, status: int, body: dict[str, object]) -> None:
        self._responses.append((status, json.dumps(body)))

    def __call__(self, method: str, url: str, headers: dict[str, str], body: bytes | None) -> TransportResponse:
        self.calls.append((method, url, headers, body))
        if not self._responses:
            raise AssertionError("No more mocked HTTP responses queued.")
        return self._responses.popleft()


def _make_client(
    environment: TrepsEnvironment = TrepsEnvironment.SANDBOX, base_url: str | None = None
) -> tuple[TrepsClient, _FakeTransport]:
    transport = _FakeTransport()
    client = TrepsClient(
        username="user",
        password="pass",
        merchant_id=1,
        environment=environment,
        base_url=base_url,
        transport=transport,
    )
    return client, transport


def _login_body(access_token: str, expire_in_ms: int) -> dict[str, object]:
    return {
        "status": True,
        "message": None,
        "data": {
            "access_token": access_token,
            "expire_in": expire_in_ms,
            "scheme": "Bearer",
            "token_policy": "apiuser",
        },
        "errors": None,
    }


def test_logs_in_once_and_reuses_the_cached_token_across_multiple_requests() -> None:
    client, transport = _make_client()
    transport.enqueue(200, _login_body("token-1", _now_ms() + 60_000))
    transport.enqueue(200, {"status": True, "message": None, "data": {"ok": 1}, "errors": None})
    transport.enqueue(200, {"status": True, "message": None, "data": {"ok": 2}, "errors": None})

    client.request("GET", "/api/whatever")
    client.request("GET", "/api/whatever")

    assert len(transport.calls) == 3  # 1 login + 2 requests
    assert transport.calls[0][1] == "https://poapi.treps.tr/api/auth"
    assert transport.calls[1][2]["Authorization"] == "Bearer token-1"


def test_re_authenticates_once_the_cached_token_has_expired() -> None:
    client, transport = _make_client()
    transport.enqueue(200, _login_body("token-1", _now_ms() - 1_000))
    transport.enqueue(200, {"status": True, "message": None, "data": {"ok": 1}, "errors": None})
    transport.enqueue(200, _login_body("token-2", _now_ms() + 60_000))
    transport.enqueue(200, {"status": True, "message": None, "data": {"ok": 2}, "errors": None})

    client.request("GET", "/api/whatever")
    client.request("GET", "/api/whatever")

    assert len(transport.calls) == 4  # login, request, re-login, request
    assert transport.calls[3][2]["Authorization"] == "Bearer token-2"


def test_throws_treps_api_error_when_the_api_returns_status_false() -> None:
    client, transport = _make_client()
    transport.enqueue(200, _login_body("token-1", _now_ms() + 60_000))
    transport.enqueue(
        200,
        {"status": False, "message": "insufficient_balance", "data": None, "errors": ["insufficient_balance"]},
    )

    with pytest.raises(TrepsApiError):
        client.request("POST", "/api/payment/pay", {})


def test_throws_treps_api_error_on_non_2xx_http_responses() -> None:
    client, transport = _make_client()
    transport.enqueue(
        401,
        {
            "status": False,
            "message": "invalid_username_or_password",
            "data": None,
            "errors": ["invalid_username_or_password"],
        },
    )

    with pytest.raises(TrepsApiError):
        client.request("GET", "/api/whatever")


def test_uses_the_production_base_url_when_environment_is_production() -> None:
    client, transport = _make_client(environment=TrepsEnvironment.PRODUCTION)
    transport.enqueue(200, _login_body("token-1", _now_ms() + 60_000))
    transport.enqueue(200, {"status": True, "message": None, "data": {}, "errors": None})

    client.request("GET", "/api/whatever")

    assert transport.calls[0][1] == "https://api.treps.io/api/auth"


def test_respects_a_custom_base_url_override() -> None:
    client, transport = _make_client(base_url="https://custom.example.com")
    transport.enqueue(200, _login_body("token-1", _now_ms() + 60_000))
    transport.enqueue(200, {"status": True, "message": None, "data": {}, "errors": None})

    client.request("GET", "/api/whatever")

    assert transport.calls[0][1] == "https://custom.example.com/api/auth"
