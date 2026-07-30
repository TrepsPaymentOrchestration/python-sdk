"""Asynchronous report download jobs (`/api/downloadjob/*`). Currently the only producer of
these jobs is `client.marketplace.settlement_summary_export()` (`report_type: 1` =
SubMerchantSettlement)."""

from __future__ import annotations

from typing import TypedDict

__all__ = [
    "DownloadJobSearchRequest",
    "DownloadJob",
    "DownloadJobSearchResponseData",
]


class DownloadJobSearchRequest(TypedDict, total=False):
    """POST /api/downloadjob/search — all filters optional."""

    #: 1 = SubMerchantSettlement.
    report_type: int
    #: 0 = Pending, 1 = Processing, 2 = Completed, 3 = Failed, 4 = Cancelling, 5 = Cancelled.
    job_status: int
    page: int
    page_size: int


class DownloadJob(TypedDict):
    """One entry of `DownloadJobSearchResponseData.items`."""

    id: int
    #: 1 = SubMerchantSettlement.
    report_type: int
    report_name: str
    #: 0 = Pending, 1 = Processing, 2 = Completed, 3 = Failed, 4 = Cancelling, 5 = Cancelled.
    job_status: int
    total_row_count: int
    processed_row_count: int
    progress_percentage: float
    error_message: str | None
    insert_date: str
    started_date: str | None
    completed_date: str | None
    cancelled_date: str | None


class DownloadJobSearchResponseData(TypedDict):
    """Pagination envelope. Use a job's `id` with `client.download_jobs.download()`/`cancel()`."""

    items: list[DownloadJob]
    total_count: int
    page: int
    page_size: int
