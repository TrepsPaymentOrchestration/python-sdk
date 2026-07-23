from __future__ import annotations

from typing import TYPE_CHECKING, cast
from urllib.parse import quote

from treps.types.hosted_page import (
    HostedPageInitRequest,
    HostedPageInitResponseData,
    HostedPageQueryResponseData,
    IFrameInitRequest,
)

if TYPE_CHECKING:
    from treps.client import TrepsClient


class HostedPageResource:
    """Secure Payment Page (Hosted Page) and embedded IFrame checkout — both are the same
    `/api/payment/hostedpage` endpoint, distinguished only by `iframe_flag`. `create` (Hosted
    Page) and `create_iframe` (embedded) both return a URL/token; Treps then POSTs the result to
    your `return_url` (verify with `verify_return_url_hash`). `query` lets you poll either kind
    of session's status by its token instead of (or in addition to) relying on the return_url
    callback."""

    def __init__(self, client: TrepsClient) -> None:
        self._client = client

    def create(self, request: HostedPageInitRequest) -> HostedPageInitResponseData:
        """POST /api/payment/hostedpage with iframe_flag: 0 — full-page redirect checkout."""
        body = {**request, "iframe_flag": 0}
        return cast(HostedPageInitResponseData, self._client.request("POST", "/api/payment/hostedpage", body))

    def create_iframe(self, request: IFrameInitRequest) -> HostedPageInitResponseData:
        """POST /api/payment/hostedpage with iframe_flag: 1 — embed the returned `url` in an
        `<iframe src="...">` on `request["iframe_web_uri"]` instead of redirecting the whole page."""
        body = {**request, "iframe_flag": 1}
        return cast(HostedPageInitResponseData, self._client.request("POST", "/api/payment/hostedpage", body))

    def query(self, token: str) -> HostedPageQueryResponseData:
        """GET /api/payment/hostedpage/{token} — works for both create() and create_iframe() sessions."""
        return cast(
            HostedPageQueryResponseData,
            self._client.request("GET", f"/api/payment/hostedpage/{quote(token, safe='')}"),
        )
