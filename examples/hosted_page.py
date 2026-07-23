"""Run with: TREPS_USERNAME=... TREPS_PASSWORD=... TREPS_MERCHANT_ID=... python examples/hosted_page.py

Demonstrates creating a Secure Payment Page (Hosted Page) session and then polling its status
by token — an alternative (or complement) to relying solely on the return_url callback.
"""

from __future__ import annotations

import datetime
import os
import time

from treps import TrepsClient, TrepsEnvironment

treps = TrepsClient(
    username=os.environ.get("TREPS_USERNAME", ""),
    password=os.environ.get("TREPS_PASSWORD", ""),
    merchant_id=int(os.environ.get("TREPS_MERCHANT_ID", "0")),
    environment=TrepsEnvironment.SANDBOX,
)


def main() -> None:
    expire_date = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )

    session = treps.hosted_page.create(
        {
            "external_order_id": f"example-hpp-{int(time.time() * 1000)}",
            "amount": 2500,
            "currency": "TRY",
            "transaction_type": 1,
            "return_url": "https://example.com/payment/return",
            "min_installment": 1,
            "expire_date": expire_date,
            "customer_commission_plan_code": "",
            "lang": "tr",
            "return_button_text": "Return to store",
            "return_button_url": "https://example.com",
            "redirect_timeout": 5,
        }
    )

    print("Redirect the customer to:", session["url"])
    print("Session token (for polling):", session["token"])

    status = treps.hosted_page.query(session["token"])
    print("Order completed?", status["order"]["order_completed"])


if __name__ == "__main__":
    main()
