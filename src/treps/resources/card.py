from __future__ import annotations

from typing import TYPE_CHECKING, cast

from treps.types.card import (
    AddCardRequest,
    AddCardResponseData,
    RemoveCardRequest,
    RemoveCardResponseData,
    UpdateCardRequest,
)

if TYPE_CHECKING:
    from treps.client import TrepsClient


class CardResource:
    """Saved/tokenized card management: add, update, and remove. To search saved cards, use
    `client.query.cards()` instead — it's the same underlying `/api/card/search` endpoint,
    grouped there since it's read-only."""

    def __init__(self, client: TrepsClient) -> None:
        self._client = client

    def add(self, request: AddCardRequest) -> AddCardResponseData:
        """POST /api/Card/add — tokenizes and saves a card for later use."""
        return cast(AddCardResponseData, self._client.request("POST", "/api/Card/add", request))

    def update(self, request: UpdateCardRequest) -> bool:
        """POST /api/Card/update — updates the alias/owner name/expiry of a saved card. Note
        this endpoint returns a bare boolean, not an object, unlike every other write endpoint
        in this SDK."""
        return cast(bool, self._client.request("POST", "/api/Card/update", request))

    def remove(self, request: RemoveCardRequest) -> RemoveCardResponseData:
        """POST /api/Card/remove — deletes a saved card."""
        return cast(RemoveCardResponseData, self._client.request("POST", "/api/Card/remove", request))
