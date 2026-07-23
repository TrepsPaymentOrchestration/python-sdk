from __future__ import annotations

from typing import TypedDict


class LoginRequest(TypedDict):
    username: str
    password: str
    merchantId: int


class LoginResponseData(TypedDict):
    access_token: str
    #: Absolute expiry instant, epoch milliseconds (NOT a duration/TTL).
    expire_in: int
    scheme: str
    token_policy: str
