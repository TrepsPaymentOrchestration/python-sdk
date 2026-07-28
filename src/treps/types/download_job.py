"""Asynchronous report download jobs (`/api/downloadjob/*`). Currently the only producer of
these jobs is `client.marketplace.settlement_summary_export()` (`report_type: 1` =
SubMerchantSettlement)."""

from __future__ import annotations

from typing import Any, TypedDict

__all__ = [
    "DownloadJobSearchRequest",
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


class DownloadJobSearchResponseData(TypedDict):
    """Pagination envelope. Individual job fields beyond `report_type`/`job_status` (e.g. file
    name, created date) aren't detailed in the source API spec, so entries are left as `Any` —
    use the job's `id` with `client.download_jobs.download()`/`cancel()`."""

    items: list[Any]
    total_count: int
    page: int
    page_size: int
