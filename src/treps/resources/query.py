from __future__ import annotations

from typing import TYPE_CHECKING, cast
from urllib.parse import quote

from treps.types.query import (
    BinQueryRequest,
    BinQueryResponseData,
    CardQueryRequest,
    CardQueryResponseData,
    CustomerCommissionItemQueryResponseData,
    CustomerCommissionScheme,
    InstallmentQueryRequest,
    InstallmentQueryResponseData,
    OrderDetailQueryRequest,
    OrderDetailQueryResponseData,
    OrderReportQueryRequest,
    OrderReportQueryResponseData,
    TransactionDetailQueryRequest,
    TransactionDetailQueryResponseData,
    TransactionReportItem,
    TransactionReportQueryRequest,
)

if TYPE_CHECKING:
    from treps.client import TrepsClient


class QueryResource:
    """Read-only lookup/reporting operations: BIN lookups, transaction/order detail and
    reporting, customer commission schemes, installment options, and saved-card search."""

    def __init__(self, client: TrepsClient) -> None:
        self._client = client

    def bin(self, request: BinQueryRequest) -> BinQueryResponseData:
        """POST /api/references/bin — looks up card brand/network/country from its BIN."""
        return cast(BinQueryResponseData, self._client.request("POST", "/api/references/bin", request))

    def transaction_detail(self, request: TransactionDetailQueryRequest) -> TransactionDetailQueryResponseData:
        """POST /api/report/transaction-detail"""
        return cast(
            TransactionDetailQueryResponseData,
            self._client.request("POST", "/api/report/transaction-detail", request),
        )

    def transaction_report(self, request: TransactionReportQueryRequest | None = None) -> list[TransactionReportItem]:
        """POST /api/report/transaction-report — paginated, filterable transaction list. Returns
        a bare list — unlike `order_report()`, which wraps in {total_count, data}."""
        return cast(
            "list[TransactionReportItem]",
            self._client.request("POST", "/api/report/transaction-report", request or {}),
        )

    def order_detail(self, request: OrderDetailQueryRequest) -> OrderDetailQueryResponseData:
        """POST /api/report/order-detail — requires `external_order_id` or `order_id`."""
        return cast(OrderDetailQueryResponseData, self._client.request("POST", "/api/report/order-detail", request))

    def order_report(self, request: OrderReportQueryRequest | None = None) -> OrderReportQueryResponseData:
        """POST /api/report/order-report — paginated, filterable order list."""
        return cast(
            OrderReportQueryResponseData,
            self._client.request("POST", "/api/report/order-report", request or {}),
        )

    def customer_commissions(self) -> list[CustomerCommissionScheme]:
        """GET /api/commission/customercommission — lists your customer commission schemes."""
        return cast(
            "list[CustomerCommissionScheme]",
            self._client.request("GET", "/api/commission/customercommission"),
        )

    def customer_commission_items(self, code: str) -> CustomerCommissionItemQueryResponseData:
        """GET /api/commission/customercommissionitemcode/{code} — per-card-network commission
        rates for a scheme returned by `customer_commissions()`."""
        return cast(
            CustomerCommissionItemQueryResponseData,
            self._client.request("GET", f"/api/commission/customercommissionitemcode/{quote(code, safe='')}"),
        )

    def installments(self, request: InstallmentQueryRequest) -> InstallmentQueryResponseData:
        """POST /api/commission/getinstallmentinfo — available installment options for a card/plan."""
        return cast(
            InstallmentQueryResponseData,
            self._client.request("POST", "/api/commission/getinstallmentinfo", request),
        )

    def cards(self, request: CardQueryRequest) -> CardQueryResponseData:
        """POST /api/card/search — search saved/tokenized cards."""
        return cast(CardQueryResponseData, self._client.request("POST", "/api/card/search", request))
