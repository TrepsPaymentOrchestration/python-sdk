from __future__ import annotations

from typing import TYPE_CHECKING, cast

from treps.types.three_d_secure import (
    ThreeDSecureCompleteRequest,
    ThreeDSecureCompleteResponseData,
    ThreeDSecureInitRequest,
    ThreeDSecureInitResponseData,
)

if TYPE_CHECKING:
    from treps.client import TrepsClient


class ThreeDSecureResource:
    """3D Secure operations. `init` starts the challenge (returns an HTML form to redirect the
    customer's browser to their bank); after the bank redirects back to your `return_url`
    (verify with `verify_return_url_hash`), call `complete` to finalize the charge."""

    def __init__(self, client: TrepsClient) -> None:
        self._client = client

    def init(self, request: ThreeDSecureInitRequest) -> ThreeDSecureInitResponseData:
        """POST /api/payment/pay3d"""
        return cast(ThreeDSecureInitResponseData, self._client.request("POST", "/api/payment/pay3d", request))

    def complete(self, request: ThreeDSecureCompleteRequest) -> ThreeDSecureCompleteResponseData:
        """POST /api/payment/pay3d/complete"""
        return cast(
            ThreeDSecureCompleteResponseData,
            self._client.request("POST", "/api/payment/pay3d/complete", request),
        )
