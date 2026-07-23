from __future__ import annotations

from typing import Any, TypedDict

__all__ = [
    "PaymentLinkBuyer",
    "PaymentLinkProduct",
    "PaymentLinkCreateRequest",
    "PaymentLinkCreateResponseData",
    "PaymentLinkQueryRequest",
    "PaymentLinkQueryProduct",
    "PaymentLinkQueryBuyer",
    "PaymentLinkQueryResponseData",
    "PaymentLinkListRequest",
    "PaymentLinkListItem",
    "PaymentLinkListResponseData",
]


class PaymentLinkBuyer(TypedDict, total=False):
    customer_id: str
    name: str
    surname: str
    email: str
    phone_number: str


class PaymentLinkProduct(TypedDict, total=False):
    product_id: str
    category: str
    name: str
    price: float
    quantity: int
    description: str


class _PaymentLinkCreateRequestRequired(TypedDict):
    #: Label/name for the link.
    name: str
    #: Unique reference for the order, up to 72 chars.
    external_order_id: str
    customer_commission_plan_code: str
    amount: float
    #: ISO currency code, e.g. TRY, USD, EUR, GBP.
    currency: str
    #: Auth=1, PreAuth=2
    transaction_type: int
    min_installment: int
    #: ISO 8601 expiry for the link.
    expire_date: str


class PaymentLinkCreateRequest(_PaymentLinkCreateRequestRequired, total=False):
    """POST /api/payment/createpaylink"""

    #: Forces the 3D Secure flow.
    secure_flag: int
    max_installment: int
    #: 1 = single-use (cannot be reused after a successful payment), 0 = multi-use.
    onetime_flag: int
    vpos_code: str
    buyer: PaymentLinkBuyer
    #: Singular, unlike the `products` list used by sale/hostedpage requests.
    product: PaymentLinkProduct


class PaymentLinkCreateResponseData(TypedDict):
    token: str


class PaymentLinkQueryRequest(TypedDict):
    """POST /api/payment/getpaylink"""

    token: str


class _PaymentLinkQueryProductRequired(TypedDict):
    link_payment_id: int


class PaymentLinkQueryProduct(_PaymentLinkQueryProductRequired, total=False):
    product_id: str
    category: str
    name: str
    price: float
    quantity: int
    description: str


class _PaymentLinkQueryBuyerRequired(TypedDict):
    link_payment_id: int


class PaymentLinkQueryBuyer(_PaymentLinkQueryBuyerRequired, total=False):
    customer_id: str
    name: str
    surname: str
    email: str
    phone_number: str
    citizenship_number: str


class PaymentLinkQueryResponseData(TypedDict):
    """The docs are inconsistent about `status`: a reference panel describes 1=active/2=expired,
    but request examples and `list()`'s filter only ever show 0/1 in practice. Prefer
    `have_completed_order` and `expire_date` for real status checks."""

    name: str
    external_order_id: str
    token: str
    transaction_type: int
    secure_flag: int
    merchant_id: int
    amount: float
    customer_commission_plan_code: str
    expire_date: str
    onetime_flag: int
    created_user_id: int
    installment_options: Any
    min_installment: int
    max_installment: int
    currency: str
    reseller_id: int | None
    sub_reseller_id: int | None
    order_ids: list[str]
    #: true once at least one successful payment has been made on this link.
    have_completed_order: bool
    products: list[PaymentLinkQueryProduct]
    buyer: PaymentLinkQueryBuyer
    id: int
    status: int
    insert_date: str


class PaymentLinkListRequest(TypedDict, total=False):
    """POST /api/payment/listpaylinks — all filters are optional."""

    #: ISO 8601.
    start_date: str
    #: ISO 8601.
    end_date: str
    #: See the `status` caveat on `PaymentLinkQueryResponseData`.
    status: int
    external_order_id: str
    link_payment_id: int
    token: str


class PaymentLinkListItem(TypedDict):
    id: int
    external_order_id: str
    buyer_name: str
    buyer_surname: str
    amount: float
    currency: str
    token: str
    name: str
    reseller_id: int | None
    sub_reseller_id: int | None
    have_completed_order: bool
    expire_date: str
    status: int
    onetime_flag: int


class PaymentLinkListResponseData(TypedDict):
    page: int
    page_size: int
    total_count: int
    data: list[PaymentLinkListItem]
