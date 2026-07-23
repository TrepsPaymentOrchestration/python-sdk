"""Run with: TREPS_USERNAME=... TREPS_PASSWORD=... TREPS_MERCHANT_ID=... python examples/payment_link.py

Demonstrates creating a shareable payment link, querying its status, and listing links.
"""

from __future__ import annotations

import datetime
import os
import sys
import time

from treps import TrepsApiError, TrepsClient, TrepsEnvironment

treps = TrepsClient(
    username=os.environ.get("TREPS_USERNAME", ""),
    password=os.environ.get("TREPS_PASSWORD", ""),
    merchant_id=int(os.environ.get("TREPS_MERCHANT_ID", "0")),
    environment=TrepsEnvironment.SANDBOX,
)


def main() -> None:
    expire_date = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=30)).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )

    link = treps.payment_links.create(
        {
            "name": "Example invoice",
            "external_order_id": f"example-link-{int(time.time() * 1000)}",
            "customer_commission_plan_code": "",
            "amount": 2500,
            "currency": "TRY",
            "transaction_type": 1,
            "min_installment": 1,
            "expire_date": expire_date,
            # Single-use: the link can't be paid again once completed.
            "onetime_flag": 1,
            "buyer": {
                "customer_id": "CUST-EXAMPLE",
                "name": "Mehmet",
                "surname": "Yılmaz",
                "email": "mehmet.yilmaz@example.com",
                "phone_number": "5324567890",
            },
        }
    )

    print("Share this link (token):", link["token"])

    details = treps.payment_links.get({"token": link["token"]})
    print("have_completed_order:", details["have_completed_order"], "| status:", details["status"])

    listing = treps.payment_links.list({"token": link["token"]})
    print(f"Payment links matching this token: {listing['total_count']} total")


if __name__ == "__main__":
    try:
        main()
    except TrepsApiError as err:
        print("Treps API error:", err, err.errors, file=sys.stderr)
        sys.exit(1)
