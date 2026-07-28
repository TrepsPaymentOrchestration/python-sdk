from __future__ import annotations

from typing import TYPE_CHECKING, cast

from treps.types.common import PaymentResponseData
from treps.types.payments import (
    PostAuthRequest,
    PostAuthResponseData,
    PreAuthRequest,
    RefundOrVoidResponseData,
    RefundRequest,
    SaleRequest,
    VoidRequest,
)

if TYPE_CHECKING:
    from treps.client import TrepsClient


class PaymentsResource:
    """Financial transaction operations: sale, pre-authorization, post-authorization (capture),
    refund, and void. All map to `/api/payment/*`."""

    def __init__(self, client: TrepsClient) -> None:
        self._client = client

    def sale(self, request: SaleRequest) -> PaymentResponseData:
        """POST /api/payment/pay with transaction_type: 1 — a direct, single-step charge."""
        body = {**request, "transaction_type": 1}
        return cast(PaymentResponseData, self._client.request("POST", "/api/payment/pay", body))

    def pre_auth(self, request: PreAuthRequest) -> PaymentResponseData:
        """POST /api/payment/pay with transaction_type: 2 — reserves funds without capturing them."""
        body = {**request, "transaction_type": 2}
        return cast(PaymentResponseData, self._client.request("POST", "/api/payment/pay", body))

    def post_auth(self, request: PostAuthRequest) -> PostAuthResponseData:
        """POST /api/payment/postauth — captures a previous PreAuth, fully or partially."""
        return cast(PostAuthResponseData, self._client.request("POST", "/api/payment/postauth", request))

    def refund(self, request: RefundRequest) -> RefundOrVoidResponseData:
        """POST /api/payment/refund — refunds a previous sale/postAuth, fully or partially. For a
        marketplace (split payment) order, pass `sub_merchants` to control how the refund is
        distributed across sub-merchants instead of refunding it as a single transaction."""
        return cast(RefundOrVoidResponseData, self._client.request("POST", "/api/payment/refund", request))

    def void(self, request: VoidRequest) -> RefundOrVoidResponseData:
        """POST /api/payment/void — fully cancels a previous sale/preAuth. For a marketplace
        (split payment) order, pass `sub_merchants` to control how the void is distributed across
        sub-merchants instead of voiding it as a single transaction."""
        return cast(RefundOrVoidResponseData, self._client.request("POST", "/api/payment/void", request))
