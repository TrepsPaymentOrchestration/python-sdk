from __future__ import annotations

from typing import TypedDict

from treps.types.common import Address, Buyer, Product

__all__ = [
    "HostedPageInitRequest",
    "IFrameCssVariables",
    "IFrameInitRequest",
    "HostedPageInitResponseData",
    "HostedPageTransaction",
    "HostedPagePayment",
    "HostedPageOrderStatus",
    "HostedPageQueryResponseData",
]


class _HostedPageInitRequestRequired(TypedDict):
    #: Unique reference for the order, up to 72 chars. Critical for duplicate detection.
    external_order_id: str
    #: Decimal amount.
    amount: float
    #: ISO currency code, e.g. TRY, USD, EUR, GBP.
    currency: str
    #: Auth=1, PreAuth=2
    transaction_type: int
    #: HTTPS callback URL the result is POSTed to. HTTP is not supported.
    return_url: str
    min_installment: int
    #: ISO 8601 expiry for the payment link/token.
    expire_date: str
    customer_commission_plan_code: str
    lang: str
    #: Label for the "back to store" button shown after payment completes.
    return_button_text: str
    #: Required when return_button_text is set.
    return_button_url: str
    #: Seconds to wait before auto-redirecting after payment completes.
    redirect_timeout: int


class HostedPageInitRequest(_HostedPageInitRequestRequired, total=False):
    """POST /api/payment/hostedpage with iframe_flag: 0 (Secure Payment Page / Hosted Page).
    `iframe_flag` is set automatically by `HostedPageResource.create()`."""

    max_installment: int
    #: Forces the 3D Secure flow. If the portal requires 3D, secure_flag: 0 is rejected.
    secure_flag: int
    #: Require SMS OTP when paying with a saved card (only meaningful with save_card: true).
    stored_card_sms_otp: bool
    #: Offer the customer the option to save their card. 1 requires card_owner_customer_id.
    save_card: int
    #: Retry with an alternate POS on bank failure/timeout. Recommended.
    retry_fail: bool
    vpos_code: str
    iframe_flag: int
    #: 1 = always redirect to return_url; 0 = keep the customer on the payment page after a failure.
    redirect_after_fail_payment: int
    buyer: Buyer
    products: list[Product]
    billing_address: Address
    shipping_address: Address


#: Inline CSS customization for the embedded IFrame payment form. All keys are hyphenated,
#: matching the actual wire format used by the API (the underscored variants that appear in
#: some prose documentation are a docs inconsistency, not what the API accepts). Declared with
#: the functional TypedDict syntax since hyphens aren't valid Python identifiers.
#: `hide-*` values are the string '0' or '1', not booleans.
IFrameCssVariables = TypedDict(
    "IFrameCssVariables",
    {
        "text-color": str,
        "text-font-weight": str,
        "font-family": str,
        "font-size": str,
        "input-bg": str,
        "input-border": str,
        "input-radius": str,
        "input-padding": str,
        "input-color": str,
        "input-font-weight": str,
        "button-background-color": str,
        "button-background-color-hover": str,
        "button-color": str,
        "button-color-hover": str,
        "button-padding": str,
        "button-border": str,
        "button-border-hover": str,
        "button-width": str,
        "button-max-width": str,
        "button-transition": str,
        "button-container-text-align": str,
        "button-container-margin-top": str,
        "label-margin": str,
        "installment-border-color": str,
        "installment-selected-border-color": str,
        "installment-selected-background-color": str,
        "hide-installments": str,
        "hide-pay-button": str,
        "hide-labels": str,
    },
    total=False,
)


class _IFrameInitRequestRequired(TypedDict):
    #: Unique reference for the order, up to 50 chars.
    external_order_id: str
    amount: float
    #: ISO currency code, e.g. TRY, USD, EUR, GBP.
    currency: str
    #: Auth=1, PreAuth=2
    transaction_type: int
    #: HTTPS callback URL the result is POSTed to.
    return_url: str
    #: The URL of the web page the iframe is embedded into.
    iframe_web_uri: str


#: The wire field is the hyphenated `css-variables`, not a valid Python identifier — declared
#: separately via functional TypedDict syntax and mixed into `IFrameInitRequest` below.
_IFrameInitRequestCssVariables = TypedDict(
    "_IFrameInitRequestCssVariables",
    {"css-variables": IFrameCssVariables},
    total=False,
)


class IFrameInitRequest(_IFrameInitRequestRequired, _IFrameInitRequestCssVariables, total=False):
    """POST /api/payment/hostedpage with iframe_flag: 1 (embedded IFrame checkout).
    `iframe_flag` is set automatically by `HostedPageResource.create_iframe()`."""

    #: Forces the 3D Secure flow.
    secure_flag: int
    min_installment: int
    max_installment: int
    #: ISO 8601 expiry for the payment link/token.
    expire_date: str
    #: Retry with an alternate POS on bank failure.
    retry_fail: bool
    customer_commission_plan_code: str
    vpos_code: str
    #: UI language, e.g. 'tr'.
    lang: str
    buyer: Buyer
    products: list[Product]
    billing_address: Address
    shipping_address: Address
    iframe_flag: int


class HostedPageInitResponseData(TypedDict):
    #: URL to redirect the customer's browser to.
    url: str
    #: Token identifying this Hosted Page session; also usable to query its status.
    token: str
    expire_date: str


class HostedPageTransaction(TypedDict):
    transaction_id: str
    transaction_amount: float
    transaction_status: int
    transaction_status_code: str
    result_code: str
    result_message: str


class HostedPagePayment(TypedDict):
    payment_id: str
    transaction_type: int
    amount: float
    payment_status: int
    payment_status_code: str
    payment_status_message: str
    bank_auth_code: str
    transactions: list[HostedPageTransaction]


class HostedPageOrderStatus(TypedDict):
    payments: list[HostedPagePayment]
    order_completed: bool
    order_success_amount: float


class HostedPageQueryResponseData(TypedDict):
    """GET /api/payment/hostedpage/{token}"""

    token: str
    external_order_id: str
    oid: str
    amount: float
    currency: str
    order: HostedPageOrderStatus
