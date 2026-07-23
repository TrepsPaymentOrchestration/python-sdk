"""Low-level HTTP client for the Treps Payment Orchestration API. Handles login and token
caching; use the ``payments``, ``three_d_secure``, ``hosted_page``, ``query``, ``cards``,
``payment_links``, and ``insurance`` resource attributes built on top of it for an
endpoint-specific API.
"""

from __future__ import annotations

import json
import threading
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any

from treps.errors import TrepsApiError
from treps.resources.card import CardResource
from treps.resources.hosted_page import HostedPageResource
from treps.resources.insurance import InsuranceResource
from treps.resources.payment_link import PaymentLinkResource
from treps.resources.payments import PaymentsResource
from treps.resources.query import QueryResource
from treps.resources.three_d_secure import ThreeDSecureResource
from treps.types.auth import LoginResponseData

#: (status_code, response_body) returned by a transport call.
TransportResponse = tuple[int, str]
#: (method, url, headers, body_bytes) -> TransportResponse. Advanced/testing hook to replace
#: the default `urllib`-based transport; most callers never need this.
Transport = Callable[[str, str, dict[str, str], "bytes | None"], TransportResponse]


class TrepsEnvironment(str, Enum):
    SANDBOX = "sandbox"
    PRODUCTION = "production"


_ENVIRONMENT_BASE_URLS: dict[TrepsEnvironment, str] = {
    TrepsEnvironment.SANDBOX: "https://poapi.treps.tr",
    TrepsEnvironment.PRODUCTION: "https://api.treps.io",
}


@dataclass
class _CachedToken:
    access_token: str
    expires_at_ms: int


def _now_ms() -> int:
    return int(time.time() * 1000)


def _default_transport(method: str, url: str, headers: dict[str, str], body: bytes | None) -> TransportResponse:
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request) as response:  # noqa: S310 - fixed https:// URLs built from our own base_url
            return response.status, response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8")


class TrepsClient:
    def __init__(
        self,
        username: str,
        password: str,
        merchant_id: int,
        environment: TrepsEnvironment = TrepsEnvironment.SANDBOX,
        base_url: str | None = None,
        token_expiry_margin_ms: int = 30_000,
        transport: Transport | None = None,
    ) -> None:
        """
        Args:
            environment: Defaults to sandbox. Ignored if `base_url` is set.
            base_url: Overrides the environment preset with a custom API base URL.
            token_expiry_margin_ms: Safety margin subtracted from the token's expiry. Defaults to 30s.
            transport: Advanced/testing hook to replace the default `urllib`-based transport.
        """
        self._username = username
        self._password = password
        self._merchant_id = merchant_id
        self._token_expiry_margin_ms = token_expiry_margin_ms
        self._base_url = base_url or _ENVIRONMENT_BASE_URLS[environment]
        self._transport: Transport = transport or _default_transport
        self._cached_token: _CachedToken | None = None
        self._lock = threading.Lock()

        #: Sale, PreAuth, PostAuth, Refund, Void.
        self.payments = PaymentsResource(self)
        #: 3D Secure init/complete.
        self.three_d_secure = ThreeDSecureResource(self)
        #: Secure Payment Page (Hosted Page) create/query.
        self.hosted_page = HostedPageResource(self)
        #: BIN lookup, transaction/order detail & reporting, commissions, installments, saved cards.
        self.query = QueryResource(self)
        #: Save/update/remove a tokenized card.
        self.cards = CardResource(self)
        #: Shareable payment links (create/get/list).
        self.payment_links = PaymentLinkResource(self)
        #: Insurance-sector payments.
        self.insurance = InsuranceResource(self)

    def login(self) -> LoginResponseData:
        """Performs POST /api/auth and returns the raw response — most callers don't need this directly."""
        token = self._ensure_logged_in()
        return LoginResponseData(
            access_token=token.access_token,
            expire_in=token.expires_at_ms,
            scheme="Bearer",
            token_policy="apiuser",
        )

    def request(self, method: str, path: str, body: Any = None) -> Any:
        """GET/POST/PUT/DELETE against the Treps API with an automatically-attached,
        auto-refreshed bearer token. Returns the unwrapped `data` field of the API envelope."""
        token = self._ensure_logged_in()
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token.access_token}"}
        payload = json.dumps(body).encode("utf-8") if body is not None else None

        status, response_text = self._transport(method, self._base_url + path, headers, payload)
        parsed = self._try_parse(response_text)

        if not (200 <= status < 300) or parsed is None or parsed.get("status") is False:
            message = (parsed.get("message") if parsed else None) or f"Treps API request failed with HTTP {status}"
            raise TrepsApiError(message, status, parsed.get("errors") if parsed else None, parsed)

        return parsed.get("data")

    def _ensure_logged_in(self) -> _CachedToken:
        cached = self._cached_token
        if cached is not None and _now_ms() < cached.expires_at_ms - self._token_expiry_margin_ms:
            return cached

        with self._lock:
            cached = self._cached_token
            if cached is not None and _now_ms() < cached.expires_at_ms - self._token_expiry_margin_ms:
                return cached
            return self._perform_login()

    def _perform_login(self) -> _CachedToken:
        headers = {"Content-Type": "application/json"}
        payload = json.dumps(
            {"username": self._username, "password": self._password, "merchantId": self._merchant_id}
        ).encode("utf-8")

        status, response_text = self._transport("POST", self._base_url + "/api/auth", headers, payload)
        parsed = self._try_parse(response_text)
        data = parsed.get("data") if parsed else None

        if not (200 <= status < 300) or parsed is None or parsed.get("status") is False or not data:
            message = (parsed.get("message") if parsed else None) or f"Treps login failed with HTTP {status}"
            raise TrepsApiError(message, status, parsed.get("errors") if parsed else None, parsed)

        token = _CachedToken(access_token=data["access_token"], expires_at_ms=data["expire_in"])
        self._cached_token = token
        return token

    @staticmethod
    def _try_parse(text: str) -> dict[str, Any] | None:
        try:
            result = json.loads(text)
        except json.JSONDecodeError:
            return None
        return result if isinstance(result, dict) else None
