from __future__ import annotations

from typing import TYPE_CHECKING, cast

from treps.types.insurance import InsurancePaymentRequest, InsurancePaymentResponseData

if TYPE_CHECKING:
    from treps.client import TrepsClient


class InsuranceResource:
    """Insurance-sector payments. Per the docs site, only the initial payment (`pay`) has an
    insurance-specific request shape (a tokenized `card_insurance` reference instead of raw card
    details, plus mandatory `is_moto`). Voiding or refunding an insurance payment uses the exact
    same endpoints and request/response shapes as any other payment — use
    `client.payments.void()` / `client.payments.refund()` for those; there is nothing
    insurance-specific to wrap. (The docs site's "detached refund" entry for insurance is, as of
    this writing, byte-for-byte identical to its regular refund entry — likely a documentation
    copy/paste rather than a distinct contract — so it isn't exposed as a separate method here.)"""

    def __init__(self, client: TrepsClient) -> None:
        self._client = client

    def pay(self, request: InsurancePaymentRequest) -> InsurancePaymentResponseData:
        """POST /api/payment/pay-insurance"""
        return cast(InsurancePaymentResponseData, self._client.request("POST", "/api/payment/pay-insurance", request))
