from __future__ import annotations

from typing import TypedDict

from treps.types.common import Address, Buyer, PaymentResponseData, Product, SubMerchant

__all__ = [
    "InsuranceCard",
    "InsurancePaymentRequest",
    "InsurancePaymentResponseData",
]


class _InsuranceCardRequired(TypedDict):
    card_owner_name: str
    #: First 6-8 digits of the card.
    card_bin: str
    card_last_four: str
    #: Card owner's tax ID (VKN) or citizenship number (TCKN) — required for insurance payments.
    owner_vkn_tckn: str
    card_owner_customer_id: str


class InsuranceCard(_InsuranceCardRequired, total=False):
    """Tokenized card reference for an insurance payment — no raw card number/expiry/CVV, since
    the card was already processed elsewhere. Distinct from `Card`, used by sale/preAuth."""

    card_alias: str
    card_reference_code: str


class _InsurancePaymentRequestRequired(TypedDict):
    external_order_id: str
    amount: float
    currency: str
    installment: int
    client_ip: str
    #: Mandatory for insurance transactions — must be True.
    is_moto: bool
    card_insurance: InsuranceCard


class InsurancePaymentRequest(_InsurancePaymentRequestRequired, total=False):
    """POST /api/payment/pay-insurance — identical to `PaymentsResource.sale()`/`pre_auth()`
    except the card is a tokenized `card_insurance` reference (not raw card details), and
    `is_moto` is mandatory (must be True) rather than optional."""

    #: ManuelPos=1, LinkPayment=2, API=3, Hostedpage=4, IFrame=4
    payment_request_type: int
    #: Auth=1, PreAuth=2
    transaction_type: int
    external_transaction_id: str
    split_payment: bool
    return_url: str
    description: str
    userId: int
    vpos_code: str
    retry_fail: bool
    customer_commission_plan_code: str
    buyer: Buyer
    products: list[Product]
    billing_address: Address
    shipping_address: Address
    sub_merchants: list[SubMerchant]


class InsurancePaymentResponseData(PaymentResponseData, total=False):
    """`insurance_payment_flag`/`insurance_card_vkn_tckn`: not present in the documented example
    response for this endpoint, but present on the equivalent field set for regular `sale`
    responses — included as optional since it's the clearest actual "this was an insurance
    payment" marker found in the source docs. Verify against a live response before relying on them."""

    insurance_payment_flag: int
    insurance_card_vkn_tckn: str
