from __future__ import annotations

from typing import TypedDict

from treps.types.common import PaymentRequestBase, PaymentResponseData

__all__ = [
    "SaleRequest",
    "PreAuthRequest",
    "PostAuthRequest",
    "PostAuthResponseData",
    "RefundRequest",
    "VoidRequest",
    "RefundOrVoidResponseData",
    "PaymentResponseData",
]


class SaleRequest(PaymentRequestBase, total=False):
    """POST /api/payment/pay — transaction_type is set automatically by ``PaymentsResource.sale()``."""

    transaction_type: int


class PreAuthRequest(PaymentRequestBase, total=False):
    """POST /api/payment/pay — transaction_type is set automatically by ``PaymentsResource.pre_auth()``."""

    transaction_type: int


class _PostAuthRequestRequired(TypedDict):
    external_transaction_id: str
    #: Wire field is camelCase, unlike `client_ip` elsewhere — a real API quirk.
    clientIp: str


class PostAuthRequest(_PostAuthRequestRequired, total=False):
    """POST /api/payment/postauth"""

    #: Payment ID of the original sale/preAuth. Required if transaction_id is omitted.
    payment_id: str
    #: Transaction ID of the original sale/preAuth. Required if payment_id is omitted.
    transaction_id: str
    #: Amount to capture. Omit to capture the full original PreAuth amount.
    amount: float


class _RefundRequestRequired(TypedDict):
    external_transaction_id: str
    clientIp: str


class RefundRequest(_RefundRequestRequired, total=False):
    """POST /api/payment/refund"""

    #: Payment ID of the original sale/postAuth. Required if transaction_id is omitted.
    payment_id: str
    #: Transaction ID of the original sale/postAuth. Required if payment_id is omitted.
    transaction_id: str
    #: Amount to refund. Omit to refund the full original amount.
    amount: float
    reason: str


class _VoidRequestRequired(TypedDict):
    external_transaction_id: str
    clientIp: str


class VoidRequest(_VoidRequestRequired, total=False):
    """POST /api/payment/void"""

    #: Payment ID of the original sale/preAuth. Required if transaction_id is omitted.
    payment_id: str
    #: Transaction ID of the original sale/preAuth. Required if payment_id is omitted.
    transaction_id: str
    reason: str


class PostAuthResponseData(TypedDict):
    status: bool
    vpos_payment_id: str
    oid: str
    transaction_id: str
    merchant_id: int
    transaction_type: int
    external_transaction_id: str
    external_order_id: str
    amount: float
    preauth_amount: float
    total_postauth_amount: float
    transaction_status: int
    transaction_status_code: str
    bank_reference_id: str | None
    bank_batch_number: str | None
    result_code: str
    result_message: str | None
    parent_transaction_sub_id: int
    created_user_id: int


class RefundOrVoidResponseData(TypedDict):
    vpos_payment_id: str
    oid: str
    transaction_id: str
    merchant_id: int
    transaction_type: int
    external_transaction_id: str
    external_order_id: str
    transaction_status: int
    transaction_status_code: str
    bank_reference_id: str | None
    bank_batch_number: str | None
    result_code: str
    result_message: str | None
    parent_transaction_sub_id: int
    created_user_id: int
