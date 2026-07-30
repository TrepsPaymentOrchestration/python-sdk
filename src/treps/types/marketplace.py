"""Marketplace / split-payment types: sub-merchant management, marketplace-wide settings, the
order approve → pay/allocate → (optional) seize/refund → collect-debt lifecycle, and settlement
reporting. All map to `/api/marketplace/*`.

Note: `MarketplaceSubMerchant` here is a distinct, unrelated shape from `treps.types.common.
SubMerchant` — the latter is the small `{reference_id, amount}` split used inline on a sale/
preAuth request, while this module's sub-merchant is the full onboarded-entity record managed
via `/api/marketplace/submerchant/*`.
"""

from __future__ import annotations

from typing import Any, TypedDict

__all__ = [
    "SubMerchantAddRequest",
    "SubMerchantUpdateRequest",
    "SubMerchantGetRequest",
    "SubMerchantFindRequest",
    "SubMerchantFindResponseData",
    "MarketplaceSubMerchant",
    "MarketplaceConfigRequest",
    "MarketplaceOrderApproveItem",
    "MarketplaceOrderPayItem",
    "MarketplaceOrderPayAllocateItem",
    "MarketplaceOrderPayAllocateAllocation",
    "MarketplaceOrderPayAllocateResultItem",
    "MarketplaceOrderPayAllocateResponseData",
    "MarketplaceOrderSeizedRequest",
    "MarketplaceOrderRefundRequest",
    "MarketplaceOrderCollectDebtRequest",
    "MarketplaceOrderCancelRequest",
    "MarketplaceSettlementSummaryRequest",
    "MarketplaceSettlementSummaryItem",
    "MarketplaceSettlementSummaryResponseData",
    "MarketplaceSettlementSummaryExportFilter",
    "MarketplaceSettlementSummaryExportRequest",
    "MarketplaceSettlementDetailRequest",
    "MarketplaceSettlementDetailItem",
    "MarketplaceSettlementDetailResponseData",
]


class _SubMerchantAddRequestRequired(TypedDict):
    #: Caller-assigned, must be unique across all sub-merchants.
    reference_id: str
    name: str
    #: Firm-type enum, e.g. sole proprietorship vs. corporate.
    sole_prop_flag: int
    tax_office: str
    vkn_tckn: str
    address: str
    district: str
    province_code: str
    #: 3-letter country code, e.g. "TUR".
    country_alpha3: str
    email: str
    phone: str
    #: e.g. 1 = IBAN.
    accounting_transfer_method: int
    iban_owner_name: str
    iban: str
    contact_name: str
    contact_surname: str
    #: Valör (payout hold) day count.
    blocked_day_count: int
    #: 1 = active, 0 = passive.
    status: int


class SubMerchantAddRequest(_SubMerchantAddRequestRequired, total=False):
    """POST /api/marketplace/submerchant/add"""

    commercial_name: str
    wallet_account_code: str


class _SubMerchantUpdateRequestRequired(TypedDict):
    reference_id: str


class SubMerchantUpdateRequest(_SubMerchantUpdateRequestRequired, total=False):
    """POST /api/marketplace/submerchant/update — every field besides `reference_id` is
    optional; omit a field to leave it unchanged."""

    name: str
    commercial_name: str
    sole_prop_flag: int
    tax_office: str
    vkn_tckn: str
    address: str
    district: str
    province_code: str
    country_alpha3: str
    email: str
    phone: str
    accounting_transfer_method: int
    iban_owner_name: str
    iban: str
    wallet_account_code: str
    contact_name: str
    contact_surname: str
    blocked_day_count: int
    status: int


class SubMerchantGetRequest(TypedDict):
    """POST /api/marketplace/submerchant/get"""

    reference_id: str


class SubMerchantFindRequest(TypedDict, total=False):
    """POST /api/marketplace/submerchant/find — all filters optional."""

    reference_id: str
    reference_ids: list[str]
    name: str
    commercial_name: str
    #: 1 = BIREYSEL, 2 = SAHIS, 3 = LTD, 4 = AS, 5 = DERNEK.
    sole_prop_flag: int
    tax_office: str
    vkn_tckn: str
    district: str
    province_code: str
    #: 3-letter country code, e.g. "TUR".
    country_alpha3: str
    email: str
    phone: str
    #: 1 = IBAN, 2 = WALLET.
    accounting_transfer_method: int
    iban_owner_name: str
    iban: str
    wallet_account_code: str
    #: Not reliably honored server-side for filtering — MerchantPanel stopped sending it and
    #: filters active/inactive client-side instead; kept here for completeness.
    status: int
    page: int
    page_size: int


class MarketplaceSubMerchant(TypedDict):
    """The full sub-merchant record, as returned by `add`/`update`/`get`/`find`."""

    reference_id: str
    name: str
    commercial_name: str | None
    sole_prop_flag: int
    sole_prop_flag_desc: str
    tax_office: str
    vkn_tckn: str
    address: str
    district: str
    province_code: str
    country_alpha3: str
    email: str
    phone: str
    accounting_transfer_method: int
    accounting_transfer_method_desc: str
    iban_owner_name: str
    iban: str
    wallet_account_code: str | None
    contact_name: str
    contact_surname: str
    blocked_day_count: int
    status: int
    insert_date: str


class SubMerchantFindResponseData(TypedDict):
    items: list[MarketplaceSubMerchant]
    total_count: int
    page: int
    page_size: int


class MarketplaceConfigRequest(TypedDict):
    """POST /api/marketplace/config — sets marketplace-wide settings. There is currently no
    GET/read endpoint to fetch these values back; this is write-only."""

    #: 1 = payouts require manual approval before transfer, 0 = auto-transfer.
    payment_transfer_approve_required: int


class MarketplaceOrderApproveItem(TypedDict):
    """One entry of the batch body sent to POST /api/marketplace/order/approve (the request
    body is a bare array of these)."""

    oid: str
    sub_merchant_reference_id: str
    partial_approve: bool
    approve_amount: float


class MarketplaceOrderPayItem(TypedDict):
    """One entry of the batch body sent to POST /api/marketplace/order/pay (the request body is
    a bare array of these)."""

    oid: str
    sub_merchant_reference_id: str
    partial_pay: bool
    pay_amount: float
    payment_reference_codes: list[str]


class MarketplaceOrderPayAllocateItem(TypedDict):
    """One entry of the batch body sent to POST /api/marketplace/order/pay/allocate (the request
    body is a bare array of these)."""

    sub_merchant_reference_id: str
    amount: float
    payment_reference_codes: list[str]


class MarketplaceOrderPayAllocateAllocation(TypedDict):
    oid: str
    applied_amount: float


class MarketplaceOrderPayAllocateResultItem(TypedDict):
    sub_merchant_reference_id: str
    success: bool
    error: str | None
    allocations: list[MarketplaceOrderPayAllocateAllocation]


class MarketplaceOrderPayAllocateResponseData(TypedDict):
    """Response of POST /api/marketplace/order/pay/allocate.

    ATOMIC: this whole batch is all-or-nothing. If `success` (the top-level field) is False,
    then *none* of the rows in `items` were actually applied — even rows whose own
    `item["success"]` is True are rolled back along with everything else. Only treat a row as
    genuinely applied when both its own `item["success"]` AND this top-level `success` are True.
    """

    success: bool
    message: str | None
    items: list[MarketplaceOrderPayAllocateResultItem]


class MarketplaceOrderSeizedRequest(TypedDict):
    """POST /api/marketplace/order/seized"""

    oid: str
    sub_merchant_reference_id: str
    seized_amount: float
    seized_reason: str


class MarketplaceOrderRefundRequest(TypedDict):
    """POST /api/marketplace/order/refund"""

    oid: str
    sub_merchant_reference_id: str
    refund_amount: float
    reason: str


class MarketplaceOrderCollectDebtRequest(TypedDict):
    """POST /api/marketplace/order/collectdept (backend's literal spelling — not a typo here)."""

    oid: str
    sub_merchant_reference_id: str
    collected_amount: float


class MarketplaceOrderCancelRequest(TypedDict):
    """POST /api/marketplace/order/cancel"""

    oid: str


class MarketplaceSettlementSummaryRequest(TypedDict, total=False):
    """POST /api/marketplace/settlement/summary — all filters optional."""

    sub_merchant_reference_ids: list[str]
    page: int
    page_size: int


class MarketplaceSettlementSummaryItem(TypedDict):
    sub_merchant_reference_id: str
    total_amount: float
    total_approved: float
    total_seized: float
    total_refunded: float
    total_paid: float
    net_balance: float
    earned_balance: float
    not_earned_balance: float


class MarketplaceSettlementSummaryResponseData(TypedDict):
    items: list[MarketplaceSettlementSummaryItem]
    total_count: int
    page: int
    page_size: int


class MarketplaceSettlementSummaryExportFilter(TypedDict, total=False):
    sub_merchant_reference_ids: list[str]


class MarketplaceSettlementSummaryExportRequest(TypedDict):
    """POST /api/marketplace/settlement/summary/export — creates an asynchronous download job;
    poll/fetch it via `client.download_jobs`."""

    report_name: str
    filter: MarketplaceSettlementSummaryExportFilter


class MarketplaceSettlementDetailRequest(TypedDict, total=False):
    """POST /api/marketplace/settlement/detail — all filters optional."""

    sub_merchant_reference_ids: list[str]
    oid: str
    #: 0 = Tümü (all), 1 = Ödendi (paid), 2 = Ödenmedi (unpaid), 3 = ValörBekliyor (awaiting payout hold).
    status_filter: int
    #: ISO datetime.
    order_date_from: str
    #: ISO datetime.
    order_date_to: str
    approval_status_filter: int
    min_unpaid_amount: float
    max_unpaid_amount: float
    has_seized: bool
    has_refunded: bool
    payment_reference_code: str
    page: int
    page_size: int


class MarketplaceSettlementDetailItem(TypedDict):
    sub_merchant_reference_id: str
    oid: str
    amount: float
    approval_amount: float
    #: 0 = Yok (none), 1 = Tam (full), 2 = Kısmi (partial).
    approval_status: int
    seized_amount: float
    refunded_amount: float
    paid_amount: float
    #: 0 = Yok (none), 1 = Tam (full), 2 = Kısmi (partial).
    paid_status: int
    unpaid_amount: float
    insert_date: str
    earned_date: str
    is_earned: bool
    payment_reference_numbers: list[str]


class MarketplaceSettlementDetailResponseData(TypedDict):
    items: list[MarketplaceSettlementDetailItem]
    total_count: int
    page: int
    page_size: int


#: Response shape for order/approve, order/pay, order/seized, order/refund, order/collectdept,
#: order/cancel, config, submerchant/import, and settlement/summary/export isn't detailed in the
#: source API spec beyond the standard `{status, message, data, errors}` envelope — modeled as
#: `Any` here rather than guessed. Refine these once the backend's exact payloads are confirmed.
MarketplaceUndocumentedResponseData = Any
