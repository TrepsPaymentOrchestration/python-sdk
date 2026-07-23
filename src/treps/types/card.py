from __future__ import annotations

from typing import TypedDict

__all__ = [
    "AddCardRequest",
    "AddCardResponseData",
    "UpdateCardRequest",
    "RemoveCardRequest",
    "RemoveCardResponseData",
]


class AddCardRequest(TypedDict):
    """POST /api/Card/add — tokenizes and saves a card for later use."""

    card_owner_name: str
    customer_code: str
    card_number: str
    #: MM/YYYY
    card_expire_date: str
    card_alias: str
    card_reference_code: str


class AddCardResponseData(TypedDict):
    card_reference_code: str
    card_token: str
    card_alias: str
    card_bin: str
    card_last_four: str
    #: MM/YYYY
    card_expire_date: str
    card_network: str
    card_type: str
    card_brand: str
    bank_bic: str
    virtual_card: bool
    business_card: bool
    card_country: str
    is_installment_supported: bool


class UpdateCardRequest(TypedDict):
    """POST /api/Card/update — updates the alias/owner name/expiry of a previously saved card."""

    customer_code: str
    card_token: str
    card_alias: str
    card_owner_name: str
    #: MM/YYYY
    card_expire_date: str


class RemoveCardRequest(TypedDict):
    """POST /api/Card/remove — deletes a previously saved card."""

    customer_code: str
    card_token: str


class RemoveCardResponseData(TypedDict):
    removed: bool
