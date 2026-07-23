"""Run with: TREPS_USERNAME=... TREPS_PASSWORD=... TREPS_MERCHANT_ID=... python examples/quickstart.py

Demonstrates a direct sale followed by a full refund against the sandbox environment.
"""

from __future__ import annotations

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
    external_order_id = f"example-order-{int(time.time() * 1000)}"

    sale = treps.payments.sale(
        {
            "external_order_id": external_order_id,
            "amount": 10.5,
            "currency": "TRY",
            "installment": 1,
            "client_ip": "127.0.0.1",
            "card": {
                "card_owner_name": "Mehmet Yılmaz",
                "card_number": "5401341234567891",
                "card_expire_year": "28",
                "card_expire_month": "12",
                "card_cvv": "000",
                "card_owner_customer_id": "CUS_EXAMPLE_1",
            },
        }
    )
    print("Sale result:", sale["payment_status_message"], sale["transaction_id"])

    refund = treps.payments.refund(
        {
            "transaction_id": sale["transaction_id"],
            "external_transaction_id": f"{external_order_id}-refund",
            "clientIp": "127.0.0.1",
        }
    )
    print("Refund result:", refund["result_message"])


if __name__ == "__main__":
    try:
        main()
    except TrepsApiError as err:
        print("Treps API error:", err, err.errors, file=sys.stderr)
        sys.exit(1)
