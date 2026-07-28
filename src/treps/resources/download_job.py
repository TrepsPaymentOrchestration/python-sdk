from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from treps.types.download_job import DownloadJobSearchRequest, DownloadJobSearchResponseData

if TYPE_CHECKING:
    from treps.client import TrepsClient


class DownloadJobResource:
    """Asynchronous report download jobs (`/api/downloadjob/*`). Currently the only producer of
    these jobs is `client.marketplace.settlement_summary_export()`."""

    def __init__(self, client: TrepsClient) -> None:
        self._client = client

    def search(self, request: DownloadJobSearchRequest | None = None) -> DownloadJobSearchResponseData:
        """POST /api/downloadjob/search — paginated, filterable job list. Poll this for
        `job_status` (2 = Completed) before calling `download()`."""
        return cast(
            DownloadJobSearchResponseData,
            self._client.request("POST", "/api/downloadjob/search", request or {}),
        )

    def download(self, job_id: int) -> bytes:
        """GET /api/downloadjob/{id}/download — downloads a completed job's file as raw bytes.
        Unlike every other method in this SDK, the response is the file itself, not a JSON
        `{status, message, data, errors}` envelope — use `search()` to confirm `job_status == 2`
        (Completed) first."""
        return self._client.request_binary("GET", f"/api/downloadjob/{job_id}/download")

    def cancel(self, job_id: int) -> Any:
        """DELETE /api/downloadjob/{id}/cancel — cancels a pending/processing job."""
        return self._client.request("DELETE", f"/api/downloadjob/{job_id}/cancel")
