"""Shared shapes, mirroring the Node SDK's ``src/types/common.ts``.

TypedDicts are erased at runtime — Python 3.10 has no ``Required``/``NotRequired`` per-field
markers (those need 3.11+, or the ``typing_extensions`` backport, which would be a runtime
dependency), so optional fields are modeled with the pre-3.11 idiom instead: a ``total=True``
base class for the required fields, subclassed by a ``total=False`` class adding the optional
ones.
"""

from __future__ import annotations

from typing import Any, TypedDict


class ApiResponse(TypedDict):
    """Standard envelope returned by every Treps API endpoint. ``data``'s real shape is known
    only by the calling Resource method, which ``cast()``s it to the correct TypedDict."""

    status: bool
    message: str | None
    data: Any
    errors: list[str] | None


class _CardRequired(TypedDict):
    card_owner_name: str
    card_number: str
    card_expire_year: str
    card_expire_month: str
    card_cvv: str
    card_owner_customer_id: str


class Card(_CardRequired, total=False):
    #: Token of a previously saved card. When set, card_number/cvv/etc. may be omitted.
    hosted_card_token: str
    card_alias: str
    card_reference_code: str
    #: 1 to tokenize the card for future use.
    save_card: int


class Buyer(TypedDict, total=False):
    id: int
    status: int
    customer_id: str
    name: str
    surname: str
    citizenship_number: str
    email: str
    phone_number: str
    country: str
    city: str
    address: str
    zip_code: str


class Address(TypedDict, total=False):
    name: str
    city: str
    country: str
    address: str
    zip_code: str


class Product(TypedDict, total=False):
    product_id: str
    category: str
    name: str
    price: float
    quantity: int
    description: str


class SubMerchant(TypedDict):
    reference_id: str
    amount: float


class _PaymentRequestBaseRequired(TypedDict):
    external_order_id: str
    amount: float
    #: ISO currency code, e.g. TRY, USD, EUR, GBP.
    currency: str
    #: Number of installments. 1 = single payment.
    installment: int
    client_ip: str
    card: Card


class PaymentRequestBase(_PaymentRequestBaseRequired, total=False):
    """Shared body fields for ``sale``, ``preAuth``, and 3D Secure ``init`` — all three post to
    an /api/payment/pay* endpoint with this same shape."""

    #: ManuelPos=1, LinkPayment=2, API=3, Hostedpage=4, IFrame=4
    payment_request_type: int
    external_transaction_id: str
    split_payment: bool
    return_url: str
    description: str
    #: Wire field is camelCase (`userId`), unlike most of this object's snake_case fields — a
    #: real API quirk, not a typo. Preserved verbatim from the Node/PHP/.NET ports.
    userId: int
    #: Specific VPOS code to route through, as configured in the Treps portal.
    vpos_code: str
    #: Retry with an alternate POS on bank failure.
    retry_fail: bool
    customer_commission_plan_code: str
    #: Mail Order / Telephone Order transaction. Default: false.
    is_moto: bool
    buyer: Buyer
    products: list[Product]
    billing_address: Address
    shipping_address: Address
    sub_merchants: list[SubMerchant]


class PaymentResponseData(TypedDict):
    """Shared response fields for ``sale``, ``preAuth``, and 3D Secure ``complete``."""

    oid: str
    payment_id: str
    transaction_id: str
    transaction_type: int
    secure_flag: int
    secure_type: str | None
    bank_vpos_code: str
    external_transaction_id: str
    external_order_id: str
    amount: float
    card_amount: float
    point_amount: float
    interest_amount: float
    currency: str
    installment: int
    cost_rate: float
    sale_rate: float
    return_url: str
    client_ip: str
    payment_status: int
    payment_status_code: str
    payment_status_message: str
    bank_reference_id: str | None
    bank_auth_code: str | None
    bank_batch_number: str | None
    process_completed_date: str
    have_sub_merchant_transaction_flag: int
    created_user_id: int
    stored_card: Any
    insert_date: str
