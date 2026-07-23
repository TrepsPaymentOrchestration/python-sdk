"""Thrown for any non-2xx HTTP response, or any 2xx response whose body has ``status: false``."""

from __future__ import annotations


class TrepsApiError(Exception):
    def __init__(
        self,
        message: str,
        http_status: int,
        errors: list[str] | None,
        response_body: object,
    ) -> None:
        super().__init__(message)
        self.http_status = http_status
        self.errors = errors
        self.response_body = response_body
