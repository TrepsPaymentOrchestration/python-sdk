from __future__ import annotations

from typing import TypedDict

from treps.types.common import Address, Buyer, Card, PaymentResponseData, Product, SubMerchant

__all__ = [
    "ThreeDSecureInitRequest",
    "ThreeDSecureInitResponseData",
    "ThreeDSecureCompleteRequest",
    "ThreeDSecureCompleteResponseData",
    "ReturnUrlPayload",
]


class _ThreeDSecureInitRequestRequired(TypedDict):
    external_order_id: str
    amount: float
    currency: str
    installment: int
    client_ip: str
    card: Card
    #: Required here, unlike the optional `return_url` on the plain `PaymentRequestBase`.
    return_url: str


class ThreeDSecureInitRequest(_ThreeDSecureInitRequestRequired, total=False):
    """POST /api/payment/pay3d — same body as `SaleRequest`, but return_url is required."""

    transaction_type: int
    payment_request_type: int
    external_transaction_id: str
    split_payment: bool
    description: str
    userId: int
    vpos_code: str
    retry_fail: bool
    customer_commission_plan_code: str
    is_moto: bool
    buyer: Buyer
    products: list[Product]
    billing_address: Address
    shipping_address: Address
    sub_merchants: list[SubMerchant]


class ThreeDSecureInitResponseData(TypedDict):
    #: Base64-encoded HTML auto-submit form that POSTs the customer's browser to the bank's 3DS page.
    redirect_content: str
    oid: str
    external_order_id: str


class ThreeDSecureCompleteRequest(TypedDict):
    """POST /api/payment/pay3d/complete"""

    oid: str
    payment_id: str
    transaction_id: str


ThreeDSecureCompleteResponseData = PaymentResponseData


class _ReturnUrlPayloadRequired(TypedDict):
    threeD_status: str
    oid: str
    payment_id: str
    transaction_id: str
    order_amount: str
    amount: str
    installment: str
    currency: str
    complete_required: str
    duplicate_request: str
    payment_status: int
    threeD_secure_type: str
    return_url: str
    hash: str


class ReturnUrlPayload(_ReturnUrlPayloadRequired, total=False):
    """Fields posted by the bank to the merchant's return_url after a 3D Secure (or Hosted
    Page) flow completes. Verify the `hash` field with `verify_return_url_hash()` before
    trusting any of these values — never trust `threeD_status == "SUCCESS"` alone."""

    external_order_id: str
    external_transaction_id: str
    card_amount: str
    interest_amount: str
    point_amount: str
    wallet_amount: str
    external_wallet_account_id: str
    wallet_payment_id: str
    wallet_cashback: str
    retry_fail: str
    retry_count: str
