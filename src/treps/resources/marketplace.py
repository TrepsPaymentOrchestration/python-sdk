from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from treps.types.marketplace import (
    MarketplaceConfigRequest,
    MarketplaceOrderApproveItem,
    MarketplaceOrderCancelRequest,
    MarketplaceOrderCollectDebtRequest,
    MarketplaceOrderPayAllocateItem,
    MarketplaceOrderPayAllocateResponseData,
    MarketplaceOrderPayItem,
    MarketplaceOrderRefundRequest,
    MarketplaceOrderSeizedRequest,
    MarketplaceSettlementDetailRequest,
    MarketplaceSettlementDetailResponseData,
    MarketplaceSettlementSummaryExportRequest,
    MarketplaceSettlementSummaryRequest,
    MarketplaceSettlementSummaryResponseData,
    MarketplaceSubMerchant,
    SubMerchantAddRequest,
    SubMerchantFindRequest,
    SubMerchantFindResponseData,
    SubMerchantGetRequest,
    SubMerchantUpdateRequest,
)

if TYPE_CHECKING:
    from treps.client import TrepsClient


class MarketplaceResource:
    """Marketplace / split-payment operations: manage sub-merchants, configure marketplace-wide
    settings, drive an order through its approve -> pay/allocate -> (optional) seize/refund ->
    collect-debt lifecycle, and report on settlement status. All map to `/api/marketplace/*`.

    To split a refund/void across sub-merchants for a marketplace order, use
    `client.payments.refund()`/`client.payments.void()` with their `sub_merchants` field instead
    — that isn't duplicated here.
    """

    def __init__(self, client: TrepsClient) -> None:
        self._client = client

    # -- Sub-merchants ----------------------------------------------------

    def submerchant_add(self, request: SubMerchantAddRequest) -> MarketplaceSubMerchant:
        """POST /api/marketplace/submerchant/add"""
        return cast(
            MarketplaceSubMerchant,
            self._client.request("POST", "/api/marketplace/submerchant/add", request),
        )

    def submerchant_update(self, request: SubMerchantUpdateRequest) -> MarketplaceSubMerchant:
        """POST /api/marketplace/submerchant/update — every field besides `reference_id` is
        optional; omit a field to leave it unchanged."""
        return cast(
            MarketplaceSubMerchant,
            self._client.request("POST", "/api/marketplace/submerchant/update", request),
        )

    def submerchant_get(self, request: SubMerchantGetRequest) -> MarketplaceSubMerchant:
        """POST /api/marketplace/submerchant/get"""
        return cast(
            MarketplaceSubMerchant,
            self._client.request("POST", "/api/marketplace/submerchant/get", request),
        )

    def submerchant_find(self, request: SubMerchantFindRequest | None = None) -> SubMerchantFindResponseData:
        """POST /api/marketplace/submerchant/find — paginated, filterable search."""
        return cast(
            SubMerchantFindResponseData,
            self._client.request("POST", "/api/marketplace/submerchant/find", request or {}),
        )

    def submerchant_import(self, request: list[SubMerchantAddRequest]) -> Any:
        """POST /api/marketplace/submerchant/import — bulk-creates sub-merchants; the request
        body is a bare array of `submerchant/add`-shaped objects. Response shape isn't detailed
        in the source API spec."""
        return self._client.request("POST", "/api/marketplace/submerchant/import", request)

    # -- Marketplace-wide settings ------------------------------------------

    def config(self, request: MarketplaceConfigRequest) -> Any:
        """POST /api/marketplace/config — sets marketplace-wide settings (currently just
        `payment_transfer_approve_required`). Write-only: there is no corresponding GET/read
        endpoint to fetch the current value back, by backend design."""
        return self._client.request("POST", "/api/marketplace/config", request)

    # -- Orders -------------------------------------------------------------

    def order_approve(self, request: list[MarketplaceOrderApproveItem]) -> Any:
        """POST /api/marketplace/order/approve — batch; the request body is a bare array."""
        return self._client.request("POST", "/api/marketplace/order/approve", request)

    def order_pay(self, request: list[MarketplaceOrderPayItem]) -> Any:
        """POST /api/marketplace/order/pay — batch; the request body is a bare array."""
        return self._client.request("POST", "/api/marketplace/order/pay", request)

    def order_pay_allocate(
        self, request: list[MarketplaceOrderPayAllocateItem]
    ) -> MarketplaceOrderPayAllocateResponseData:
        """POST /api/marketplace/order/pay/allocate — batch; the request body is a bare array.

        ATOMIC: if the response's top-level `success` is False, NONE of the rows in `items` were
        actually applied, even if a given row's own `success` looks True — the entire batch is
        rolled back together. Only treat a row as genuinely applied when both its own
        `item["success"]` AND the top-level `success` are True.
        """
        return cast(
            MarketplaceOrderPayAllocateResponseData,
            self._client.request("POST", "/api/marketplace/order/pay/allocate", request),
        )

    def order_seized(self, request: MarketplaceOrderSeizedRequest) -> Any:
        """POST /api/marketplace/order/seized"""
        return self._client.request("POST", "/api/marketplace/order/seized", request)

    def order_refund(self, request: MarketplaceOrderRefundRequest) -> Any:
        """POST /api/marketplace/order/refund — refunds a marketplace order at the sub-merchant
        level. For splitting a `client.payments.refund()` across sub-merchants instead, use that
        method's `sub_merchants` field."""
        return self._client.request("POST", "/api/marketplace/order/refund", request)

    def order_collect_debt(self, request: MarketplaceOrderCollectDebtRequest) -> Any:
        """POST /api/marketplace/order/collectdept (backend's literal spelling, not a typo here)."""
        return self._client.request("POST", "/api/marketplace/order/collectdept", request)

    def order_cancel(self, request: MarketplaceOrderCancelRequest) -> Any:
        """POST /api/marketplace/order/cancel — cancels/voids a marketplace order at the
        sub-merchant level. For splitting a `client.payments.void()` across sub-merchants
        instead, use that method's `sub_merchants` field."""
        return self._client.request("POST", "/api/marketplace/order/cancel", request)

    # -- Settlement reporting -------------------------------------------------

    def settlement_summary(
        self, request: MarketplaceSettlementSummaryRequest | None = None
    ) -> MarketplaceSettlementSummaryResponseData:
        """POST /api/marketplace/settlement/summary — paginated, per-sub-merchant balance summary."""
        return cast(
            MarketplaceSettlementSummaryResponseData,
            self._client.request("POST", "/api/marketplace/settlement/summary", request or {}),
        )

    def settlement_summary_export(self, request: MarketplaceSettlementSummaryExportRequest) -> Any:
        """POST /api/marketplace/settlement/summary/export — creates an asynchronous download
        job for the settlement summary report; poll and fetch it via `client.download_jobs`
        (`report_type: 1` = SubMerchantSettlement)."""
        return self._client.request("POST", "/api/marketplace/settlement/summary/export", request)

    def settlement_detail(
        self, request: MarketplaceSettlementDetailRequest | None = None
    ) -> MarketplaceSettlementDetailResponseData:
        """POST /api/marketplace/settlement/detail — paginated, filterable per-order settlement
        detail (approval/seize/refund/paid amounts and status)."""
        return cast(
            MarketplaceSettlementDetailResponseData,
            self._client.request("POST", "/api/marketplace/settlement/detail", request or {}),
        )
