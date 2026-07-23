from __future__ import annotations

from typing import TYPE_CHECKING, cast

from treps.types.payment_link import (
    PaymentLinkCreateRequest,
    PaymentLinkCreateResponseData,
    PaymentLinkListRequest,
    PaymentLinkListResponseData,
    PaymentLinkQueryRequest,
    PaymentLinkQueryResponseData,
)

if TYPE_CHECKING:
    from treps.client import TrepsClient


class PaymentLinkResource:
    """Shareable payment links (email/SMS/WhatsApp) — the customer completes payment on a
    Treps-hosted page reached via the link, no card details ever touch your servers."""

    def __init__(self, client: TrepsClient) -> None:
        self._client = client

    def create(self, request: PaymentLinkCreateRequest) -> PaymentLinkCreateResponseData:
        """POST /api/payment/createpaylink"""
        return cast(
            PaymentLinkCreateResponseData,
            self._client.request("POST", "/api/payment/createpaylink", request),
        )

    def get(self, request: PaymentLinkQueryRequest) -> PaymentLinkQueryResponseData:
        """POST /api/payment/getpaylink — full details + payment status for a link, by its token."""
        return cast(PaymentLinkQueryResponseData, self._client.request("POST", "/api/payment/getpaylink", request))

    def list(self, request: PaymentLinkListRequest | None = None) -> PaymentLinkListResponseData:
        """POST /api/payment/listpaylinks — paginated, filterable list of payment links."""
        return cast(
            PaymentLinkListResponseData,
            self._client.request("POST", "/api/payment/listpaylinks", request or {}),
        )
