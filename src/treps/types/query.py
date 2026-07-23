from __future__ import annotations

from typing import Any, TypedDict

__all__ = [
    "BinQueryRequest",
    "BinQueryResponseData",
    "TransactionDetailQueryRequest",
    "TransactionDetailQueryResponseData",
    "TransactionReportQueryRequest",
    "TransactionReportItem",
    "OrderDetailQueryRequest",
    "OrderDetailAddress",
    "OrderDetailProduct",
    "OrderDetailPayment",
    "OrderDetailBuyer",
    "OrderDetailOrder",
    "OrderDetailQueryResponseData",
    "OrderReportQueryRequest",
    "OrderReportItem",
    "OrderReportQueryResponseData",
    "CustomerCommissionScheme",
    "CustomerCommissionItem",
    "CustomerCommissionItemQueryResponseData",
    "InstallmentQueryRequest",
    "InstallmentOption",
    "InstallmentQueryResponseData",
    "CardQueryRequest",
    "SavedCard",
    "CardQueryResponseData",
]


class BinQueryRequest(TypedDict):
    """POST /api/references/bin"""

    #: The card's BIN, first 6-8 digits.
    card_bin: str


class BinQueryResponseData(TypedDict):
    bank_bic: str
    card_brand: str
    card_network: str
    card_country: str
    card_type: str
    business_card: bool
    virtual_card: bool
    is_installment_supported: bool


class TransactionDetailQueryRequest(TypedDict):
    """POST /api/report/transaction-detail"""

    transaction_id: str


class TransactionDetailQueryResponseData(TypedDict):
    vpos_payment_id: str
    oid: str
    transaction_id: str
    merchant_id: int
    transaction_type: int
    secure_flag: int
    hosted_card_token: str
    external_transaction_id: str
    external_order_id: str
    transaction_amount: float
    transaction_status: int
    transaction_status_code: str | None
    bank_reference_id: str | None
    bank_batch_number: str | None
    result_code: str | None
    result_message: str | None
    parent_transaction_sub_id: int
    created_user_id: int
    id: int
    status: int
    insert_date: str
    card_owner_name: str
    card_bank_owner_name: str
    card_bin: str
    card_last_four: str
    card_number: str | None
    card_country_code: str
    card_bank_code: str
    card_type: str
    card_network: str
    bank_id: int
    bank_vpos_id: int
    bank_vpos_code: str
    customer_id: str | None


class TransactionReportQueryRequest(TypedDict, total=False):
    """POST /api/report/transaction-report. All filters optional."""

    page: int
    page_size: int
    #: ISO 8601.
    start_date: str
    #: ISO 8601.
    end_date: str
    #: e.g. 1 = Sale.
    transaction_type: int
    #: e.g. 10 = Successful.
    transaction_status: int
    card_bin: str
    card_last_four: str
    #: 1 = yes, 0 = no.
    is_3d: int
    #: 1 = yes, 0 = no. Keeps the documented inner-capital-C spelling.
    is_savedCard: int
    vpos_id: str


class TransactionReportItem(TypedDict):
    merchant_id: int
    transaction_type: str
    vpos_id: str
    transaction_id: str
    vpos_code: str
    external_oid: str
    oid: str
    bank_auth_code: str
    bank_batch_number: str
    status: str
    payment_status: str
    payment_id: str
    transaction_date: str
    order_date: str
    payment_date: str
    transaction_amount: float
    total: float
    customer_id: str | None
    customer_email: str | None
    customer_name: str | None
    card_bank: str
    card_type: str
    card_bin: str
    card_last_four: str
    is_saved_card: bool
    is_secure: int
    secure_result: str | None
    result_code: str
    result_message: str
    bank_reference_id: str
    bank_id: int
    currency: str


class OrderDetailQueryRequest(TypedDict, total=False):
    """POST /api/report/order-detail. `external_order_id` or `order_id` is required."""

    external_order_id: str
    order_id: str


class OrderDetailAddress(TypedDict):
    order_id: int
    #: Address type, e.g. 1 = billing.
    type: int
    city: str
    country: str
    address: str


class OrderDetailProduct(TypedDict):
    order_id: int
    product_id: str
    category: str
    name: str
    price: float
    quantity: int


class OrderDetailPayment(TypedDict):
    bank_reference_id: str | None
    bank_batch_number: str | None
    payment_request_type: int
    created_user_id: int
    order_db_id: int
    oid: str
    merchant_id: int
    interest_amount: float
    #: Documented field name as-is (looks like a typo-ish duplicate of result_message).
    result_message2: str | None
    card_network: str
    card_owner_name: str
    secure_flag: int
    bank_id: int | None
    payment_id: str
    external_transaction_id: str
    card_last_four: str
    payment_status_code: str
    payment_status_message: str | None
    amount: float
    payment_date: str
    card_bin: str
    sale_rate: float
    result_message: str
    bank_auth_code: str
    payment_status: int
    payment_type: int
    is_saved_card: bool


class OrderDetailBuyer(TypedDict):
    order_id: int
    customer_id: str | None
    email: str | None
    phone_number: str | None
    country: str | None
    city: str | None


class OrderDetailOrder(TypedDict):
    oid: str
    external_order_id: str
    buyer: OrderDetailBuyer
    addresses: list[OrderDetailAddress]
    products: list[OrderDetailProduct]
    sub_merchants: list[Any]
    #: Always empty in practice — the populated list is `payments` at the top level below.
    payments: list[OrderDetailPayment]
    order_db_id: int
    order_date: str
    merchant_id: int


class OrderDetailQueryResponseData(TypedDict):
    order: OrderDetailOrder
    payments: list[OrderDetailPayment]


class OrderReportQueryRequest(TypedDict, total=False):
    """POST /api/report/order-report. All filters optional."""

    page: int
    page_size: int
    external_order_id: str
    #: ISO 8601.
    start_date: str
    #: ISO 8601.
    end_date: str


class OrderReportItem(TypedDict):
    merchant_id: int | None
    external_order_id: str
    oid: str
    bank_batch_number: str | None
    payment_status: int
    secure_flag: int
    payment_id: str
    payment_type: int
    order_date: str
    payment_date: str
    amount: float
    customer_id: str | None
    customer_email: str | None
    card_holder_name: str
    bank_reference_id: str | None
    currency: str
    bank_vpos_code: str
    bank_vpos_id: int


class OrderReportQueryResponseData(TypedDict):
    total_count: int
    data: list[OrderReportItem]


class CustomerCommissionScheme(TypedDict):
    id: int
    entity_id: int
    merchant_id: int
    name: str
    code: str
    separate_card_brands_flag: int
    eff_start_date: str
    eff_end_date: str
    items: Any


class CustomerCommissionItem(TypedDict):
    currency: str
    installment_cnt: int
    card_brand_code: str
    card_network: str
    card_country_code: str
    commission_rate: float


class CustomerCommissionItemQueryResponseData(TypedDict):
    """GET /api/commission/customercommissionitemcode/{code}"""

    id: int
    entity_id: int
    merchant_id: int
    name: str
    code: str
    separate_card_brands_flag: int
    eff_start_date: str
    eff_end_date: str
    items: list[CustomerCommissionItem]


class _InstallmentQueryRequestRequired(TypedDict):
    #: Card BIN, first 6-8 digits. Documented as a number elsewhere but examples send it as a
    #: string — use a string.
    bin: str
    #: e.g. TRY, USD, EUR, GBP.
    currency: str
    #: Customer's installment plan code. Pass an empty string to only get the single-payment
    #: (peşin) option.
    planCode: str


class InstallmentQueryRequest(_InstallmentQueryRequestRequired, total=False):
    """POST /api/commission/getinstallmentinfo"""

    amount: float
    #: Restrict to a specific VPOS's installment options.
    vposCode: str


class InstallmentOption(TypedDict):
    installment_price: float
    total_price: float
    installment_cnt: int


class InstallmentQueryResponseData(TypedDict):
    amount: float
    brand: str
    network: str
    country: str
    currency: str
    force3ds: bool
    installments: list[InstallmentOption]


class _CardQueryRequestRequired(TypedDict):
    customer_code: str


class CardQueryRequest(_CardQueryRequestRequired, total=False):
    """POST /api/card/search — searches saved/tokenized cards."""

    card_token: str
    #: Not in the documented parameter table, but accepted (mirrors the response's card_owner_name).
    card_owner_name: str
    card_alias: str
    card_bin: str
    card_last_four: str
    #: MM/YYYY
    card_expire_begin: str
    #: MM/YYYY
    card_expire_end: str
    card_network: str
    card_type: str
    card_brand: str
    card_bank_bic: str
    #: Not in the documented parameter table, but accepted (mirrors the response's card_reference_code).
    card_reference_code: str
    #: ISO 8601.
    create_date_begin: str
    #: ISO 8601.
    create_date_end: str
    page: int
    page_size: int


class SavedCard(TypedDict):
    customer_code: str
    merchant_id: int
    card_token: str
    card_network: str
    card_type: str
    card_country: str
    create_date: str
    bank_bic: str
    card_brand: str
    business_card: bool
    virtual_card: bool
    card_owner_name: str
    card_reference_code: str
    card_alias: str
    card_bin: str
    card_last_four: str
    #: MM/YYYY
    card_expire_date: str
    is_installment_supported: bool


class CardQueryResponseData(TypedDict):
    page: int
    page_size: int
    total_count: int
    cards: list[SavedCard]
