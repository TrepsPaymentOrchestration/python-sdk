# treps-sdk

Official Python SDK for the **Treps Payment Orchestration Platform**.

[![CI](https://github.com/TrepsPaymentOrchestration/python-sdk/actions/workflows/ci.yml/badge.svg)](https://github.com/TrepsPaymentOrchestration/python-sdk/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/treps-sdk.svg)](https://pypi.org/project/treps-sdk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

This v0.1 release covers the core integration flows: **Authentication**, **Financial
Transactions** (sale / pre-auth / post-auth / refund / void), **3D Secure**, the
**Secure Payment Page** (Hosted Page) and its **embedded IFrame** variant, **Query
Operations** (BIN lookup, transaction/order detail & reporting, commissions, installments,
saved-card search), **Card Operations** (add / update / remove a tokenized card), **Payment
Links**, **Insurance-sector Payments**, and **Marketplace / Split Payments** (sub-merchant
management, order approve/pay/allocate/seize/refund/collect-debt/cancel lifecycle, settlement
reporting, and asynchronous report downloads). See [Roadmap](#roadmap) for what's next.

Full API reference: **[REPLACE ME: public docs site URL]** (Transaction Types, 3D Secure,
Secure Payment Page, and Hash Verification pages).

## Install

```bash
pip install treps-sdk
```

Requires Python 3.10 or newer (uses the standard library's `urllib` — zero runtime dependencies).

## Quickstart

```python
import os
from treps import TrepsClient, TrepsEnvironment

treps = TrepsClient(
    username=os.environ["TREPS_USERNAME"],
    password=os.environ["TREPS_PASSWORD"],
    merchant_id=int(os.environ["TREPS_MERCHANT_ID"]),
    environment=TrepsEnvironment.SANDBOX,  # or TrepsEnvironment.PRODUCTION
)

result = treps.payments.sale(
    {
        "external_order_id": "ORDER-1001",
        "amount": 800.5,
        "currency": "TRY",
        "installment": 1,
        "client_ip": "192.168.1.105",
        "card": {
            "card_owner_name": "Mehmet Evirgen",
            "card_number": "5401341234567891",
            "card_expire_year": "28",
            "card_expire_month": "12",
            "card_cvv": "000",
            "card_owner_customer_id": "CUS_78945612",
        },
    }
)

print(result["payment_status"], result["payment_status_message"])
```

The client authenticates lazily (on first request) and caches the token, re-authenticating
automatically once it expires — you never call `login()` yourself unless you want to warm the
cache up front.

Requests and responses are plain `dict`s typed as `TypedDict`s — every SDK method has type hints
that give you IDE autocomplete and static-analysis checking (via `mypy`/`pyright`) without a
runtime class per endpoint.

## Financial transactions

```python
treps.payments.sale({...})  # direct charge
treps.payments.pre_auth({...})  # reserve funds
treps.payments.post_auth({"transaction_id": tx_id, "external_transaction_id": ext_id, "clientIp": ip})  # capture
treps.payments.refund(
    {"transaction_id": tx_id, "external_transaction_id": ext_id, "clientIp": ip}
)  # full/partial refund
treps.payments.void({"transaction_id": tx_id, "external_transaction_id": ext_id, "clientIp": ip})  # full cancellation
```

`post_auth`, `refund`, and `void` each accept either `payment_id` or `transaction_id` to
identify the original transaction. Note these three use `clientIp` (camelCase); every other
request shape uses `client_ip` (snake_case) — a real asymmetry in the underlying API, not a typo.

## 3D Secure

```python
init = treps.three_d_secure.init(
    {
        "external_order_id": "ORDER-1002",
        "amount": 100,
        "currency": "TRY",
        "installment": 1,
        "client_ip": client_ip,
        "return_url": "https://your-site.com/payment/return",
        "card": {...},
    }
)

# init["redirect_content"] is a base64-encoded HTML auto-submit form.
# Decode it and render it to redirect the customer's browser to their bank.
```

After the bank redirects back to your `return_url`, **verify the callback before trusting
it**, then complete the charge:

```python
from treps import verify_return_url_hash

# In your return_url route handler, build a dict from the posted form/query fields.
is_valid = verify_return_url_hash(return_url_fields, os.environ["TREPS_3D_SECURITY_KEY"])
if not is_valid or return_url_fields["threeD_status"] != "SUCCESS":
    return redirect("/payment/failed")

result = treps.three_d_secure.complete(
    {
        "oid": return_url_fields["oid"],
        "payment_id": return_url_fields["payment_id"],
        "transaction_id": return_url_fields["transaction_id"],
    }
)

# finalize the order using result
```

> **Never** trust `threeD_status == "SUCCESS"` without a passing `verify_return_url_hash()`
> check first — the callback is a plain HTTP POST from the customer's browser and can be
> forged without it.

## Secure Payment Page (Hosted Page)

Let Treps host the entire payment form — redirect the customer to a URL instead of
collecting card details yourself:

```python
session = treps.hosted_page.create(
    {
        "external_order_id": "ORDER-1003",
        "amount": 2500,
        "currency": "TRY",
        "transaction_type": 1,
        "return_url": "https://your-site.com/payment/return",
        "min_installment": 1,
        "expire_date": "2026-12-31T23:59:59Z",
        "customer_commission_plan_code": "",
        "lang": "tr",
        "return_button_text": "Return to store",
        "return_button_url": "https://your-site.com",
        "redirect_timeout": 5,
    }
)

# redirect the customer to session["url"]
```

The result is POSTed to your `return_url` the same way as the 3D Secure flow above (verify
with `verify_return_url_hash()` first). You can also poll a session's status directly:

```python
status = treps.hosted_page.query(session["token"])
print(status["order"]["order_completed"], status["order"]["order_success_amount"])
```

### Embedded IFrame checkout

Same endpoint, `iframe_flag: 1` — embed the returned URL in an `<iframe>` on your own page
instead of redirecting to it, with optional inline styling:

```python
session = treps.hosted_page.create_iframe(
    {
        "external_order_id": "ORDER-1004",
        "amount": 2500,
        "currency": "TRY",
        "transaction_type": 1,
        "return_url": "https://your-site.com/payment/return",
        "iframe_web_uri": "https://your-site.com/checkout",
        "lang": "tr",
        "css-variables": {
            "button-background-color": "#10b981",
            "font-family": "Segoe UI, Roboto, sans-serif",
        },
    }
)

# <iframe src="{session['url']}"> on your checkout page
```

`query(session["token"])` works the same way for both `create()` and `create_iframe()`
sessions — it's the same underlying endpoint.

## Query operations

Read-only lookups and reporting — none of these trigger webhooks or change any state:

```python
# BIN lookup
bin_info = treps.query.bin({"card_bin": "43550843"})

# Transaction / order detail
tx = treps.query.transaction_detail({"transaction_id": "TRX-2-Tf8a6M5YtK"})
order = treps.query.order_detail({"external_order_id": "ORDER-1001"})

# Paginated reports
transactions = treps.query.transaction_report({"page": 1, "page_size": 100})
orders = treps.query.order_report({"page": 1, "page_size": 100})

# Commissions
schemes = treps.query.customer_commissions()
scheme = treps.query.customer_commission_items(schemes[0]["code"])

# Installment options for a card BIN + plan
installments = treps.query.installments(
    {
        "bin": "48248929",
        "currency": "TRY",
        "planCode": "Mus_01",
    }
)

# Search saved/tokenized cards
cards = treps.query.cards({"customer_code": "CARD10"})
```

## Card operations

Save, update, and remove tokenized cards (searching them is `treps.query.cards()` above,
since it's read-only):

```python
card = treps.cards.add(
    {
        "card_owner_name": "Mehmet Yılmaz",
        "customer_code": "CARD10",
        "card_number": "5406675406675403",
        "card_expire_date": "12/2040",
        "card_alias": "İş Bankası kartım",
        "card_reference_code": "ref-001",
    }
)

treps.cards.update(
    {
        "customer_code": "CARD10",
        "card_token": card["card_token"],
        "card_alias": "New alias",
        "card_owner_name": "Mehmet Yılmaz",
        "card_expire_date": "12/2040",
    }
)

treps.cards.remove({"customer_code": "CARD10", "card_token": card["card_token"]})
```

## Payment links

Create a shareable link (email/SMS/WhatsApp) that the customer opens to complete payment on a
Treps-hosted page — no card details ever touch your servers:

```python
link = treps.payment_links.create(
    {
        "name": "Invoice #1042",
        "external_order_id": "ORDER-1005",
        "customer_commission_plan_code": "",
        "amount": 2500,
        "currency": "TRY",
        "transaction_type": 1,
        "min_installment": 1,
        "expire_date": "2026-12-31T23:59:59Z",
        "onetime_flag": 1,  # single-use: can't be paid again once completed
    }
)

print(link["token"])  # share a URL built around this token, or query/list by it
```

```python
details = treps.payment_links.get({"token": link["token"]})
print(details["have_completed_order"], details["status"])

links = treps.payment_links.list({"status": 1})
```

> **Note:** the docs describe `status` inconsistently (a reference panel says `1`=active/`2`=expired,
> but real examples only ever show `0`/`1`). Prefer `have_completed_order` and `expire_date` over
> `status` for the checks that actually matter to you.

## Insurance-sector payments

The only endpoint with an insurance-specific request shape is the payment itself — it takes a
tokenized `card_insurance` reference (BIN + last four + the cardholder's tax ID) instead of raw
card details, and `is_moto` is mandatory:

```python
result = treps.insurance.pay(
    {
        "external_order_id": "ORDER-1006",
        "amount": 800.5,
        "currency": "TRY",
        "installment": 1,
        "client_ip": client_ip,
        "is_moto": True,
        "card_insurance": {
            "card_owner_name": "Mehmet Yılmaz",
            "card_bin": "12345678",
            "card_last_four": "9876",
            "owner_vkn_tckn": "1234567890",
            "card_owner_customer_id": "CUS_78945612",
        },
    }
)
```

Voiding or refunding an insurance payment uses the exact same `treps.payments.void()` /
`treps.payments.refund()` methods as any other transaction — the docs site's "insurance
void/refund" entries are, at the wire level, identical to the regular ones (its "detached
refund" variant is in turn identical to its own regular refund entry, which looks like a
documentation copy/paste rather than an intentionally distinct contract), so nothing
insurance-specific is duplicated here.

## Marketplace / split payments

Split a payment across onboarded sub-merchants and manage their whole order lifecycle:
sub-merchant onboarding, marketplace-wide settings, order approve/pay/allocate/seize/refund/
collect-debt/cancel, and settlement reporting. All map to `/api/marketplace/*`.

```python
submerchant = treps.marketplace.submerchant_add(
    {
        "reference_id": "SUB-001",
        "name": "Example Mağazası A.Ş.",
        "sole_prop_flag": 0,
        "tax_office": "Kadıköy",
        "vkn_tckn": "1234567890",
        "address": "Örnek Mah. Örnek Cad. No:1",
        "district": "Kadıköy",
        "province_code": "34",
        "country_alpha3": "TUR",
        "email": "submerchant@example.com",
        "phone": "5324567890",
        "accounting_transfer_method": 1,  # IBAN
        "iban_owner_name": "Example Mağazası A.Ş.",
        "iban": "TR330006100519786457841326",
        "contact_name": "Ayşe",
        "contact_surname": "Yılmaz",
        "blocked_day_count": 7,  # valör (payout hold) days
        "status": 1,  # active
    }
)

found = treps.marketplace.submerchant_find({"reference_id": "SUB-001"})
```

`treps.marketplace.config()` sets marketplace-wide settings (currently just
`payment_transfer_approve_required`) — it's **write-only**, there is no matching read endpoint.

A split order moves through approve, then pay (or `pay_allocate`), with optional seize/refund/
collect-debt along the way, and cancel to void it outright. `order_approve`, `order_pay`, and
`order_pay_allocate` each take a **bare array** — every element is applied against a different
`(oid, sub_merchant_reference_id)` pair in one call:

```python
treps.marketplace.order_approve(
    [{"oid": "OID-1", "sub_merchant_reference_id": "SUB-001", "partial_approve": False, "approve_amount": 100.0}]
)

result = treps.marketplace.order_pay_allocate(
    [{"sub_merchant_reference_id": "SUB-001", "amount": 100.0, "payment_reference_codes": ["PAYOUT-0001"]}]
)
```

> **`order_pay_allocate` is atomic across the whole batch.** If `result["success"]` is `False`,
> *none* of the rows in `result["items"]` were actually applied — even a row whose own
> `item["success"]` looks `True` was rolled back along with everything else. Only treat a row as
> genuinely applied when both its own `item["success"]` **and** the top-level `result["success"]`
> are `True`.

Settlement reporting, paginated and filterable:

```python
summary = treps.marketplace.settlement_summary({"sub_merchant_reference_ids": ["SUB-001"]})
detail = treps.marketplace.settlement_detail({"sub_merchant_reference_ids": ["SUB-001"]})
```

`settlement_summary_export()` kicks off an asynchronous report job instead of returning data
directly — track and fetch it with `treps.download_jobs`:

```python
treps.marketplace.settlement_summary_export(
    {"report_name": "monthly-settlement", "filter": {"sub_merchant_reference_ids": ["SUB-001"]}}
)

jobs = treps.download_jobs.search({"report_type": 1})  # 1 = SubMerchantSettlement
# once a job's job_status == 2 (Completed):
file_bytes = treps.download_jobs.download(jobs["items"][0]["id"])
```

Unlike every other method in this SDK, `download_jobs.download()` returns the raw file
(`bytes`), not a parsed JSON envelope.

To refund or void a split order, use the regular `treps.payments.refund()` / `.void()` with
their `sub_merchants` field to control the per-sub-merchant distribution — note that field is
genuinely named `reference_id` there (the request-side spelling), unlike the
`sub_merchant_reference_id` field name used throughout the marketplace response payloads above:

```python
treps.payments.refund(
    {
        "transaction_id": tx_id,
        "external_transaction_id": f"{oid}-refund",
        "clientIp": "127.0.0.1",
        "sub_merchants": [{"reference_id": "SUB-001", "refund_amount": 100.0}],
    }
)
```

## Error handling

Any failed request (non-2xx HTTP, or a 2xx response with `status: false`) raises
`treps.TrepsApiError`:

```python
from treps import TrepsApiError

try:
    treps.payments.sale({...})
except TrepsApiError as err:
    print(err, err.errors, err.http_status)
    raise
```

## Examples

Runnable, self-contained scripts under [`examples/`](./examples):

| File | Demonstrates |
| --- | --- |
| [`quickstart.py`](./examples/quickstart.py) | `sale` followed by a `refund` |
| [`three_d_secure.py`](./examples/three_d_secure.py) | `three_d_secure.init`, decoding the redirect form, and verifying + completing the `return_url` callback |
| [`hosted_page.py`](./examples/hosted_page.py) | Creating a Secure Payment Page session and polling it by token |
| [`iframe.py`](./examples/iframe.py) | Embedded IFrame checkout with custom CSS variables |
| [`query.py`](./examples/query.py) | BIN lookup, transaction/order detail, reports, commissions, installments, and card search |
| [`card.py`](./examples/card.py) | Add, update, search, and remove a saved card |
| [`payment_link.py`](./examples/payment_link.py) | Create a payment link, query its status, and list links |
| [`insurance.py`](./examples/insurance.py) | An insurance-sector payment, then refunding it via the regular refund endpoint |
| [`marketplace.py`](./examples/marketplace.py) | Sub-merchant onboarding, marketplace config, the order approve/pay-allocate lifecycle, settlement reporting, and an async report export |

```bash
TREPS_USERNAME=... TREPS_PASSWORD=... TREPS_MERCHANT_ID=... python examples/quickstart.py
```

## Environments

| Environment | Base URL |
| --- | --- |
| `TrepsEnvironment.SANDBOX` | `https://poapi.treps.tr` |
| `TrepsEnvironment.PRODUCTION` | `https://api.treps.io` |

Pass a custom `base_url` instead of `environment` to point at any other host (e.g. a local
mock server in tests), or a custom `transport` callable to control connection pooling, timeouts,
or supply your own HTTP stack (e.g. `requests`/`httpx`) instead of the default `urllib`-based one.

## Roadmap

Not yet covered by this SDK (planned as fast-follow module):

- Closed Loop Wallet

Contributions and issues are welcome — see [SECURITY.md](./SECURITY.md) for reporting
vulnerabilities specifically.

## License

[MIT](./LICENSE)
