"""Run with: TREPS_USERNAME=... TREPS_PASSWORD=... TREPS_MERCHANT_ID=... python examples/insurance.py

Demonstrates an insurance-sector payment. Note this is the only insurance-specific endpoint —
voiding or refunding an insurance payment uses treps.payments.void()/refund() exactly like any
other transaction (see quickstart.py).
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
    result = treps.insurance.pay(
        {
            "external_order_id": f"example-insurance-{int(time.time() * 1000)}",
            "amount": 800.5,
            "currency": "TRY",
            "installment": 1,
            "client_ip": "127.0.0.1",
            "is_moto": True,
            "card_insurance": {
                "card_owner_name": "Mehmet Yılmaz",
                "card_bin": "12345678",
                "card_last_four": "9876",
                "owner_vkn_tckn": "1234567890",
                "card_owner_customer_id": "CUS_EXAMPLE_INS",
            },
        }
    )

    print("Insurance payment result:", result["payment_status_message"], result["transaction_id"])

    # Refunding/voiding uses the exact same endpoints as a regular payment:
    refund = treps.payments.refund(
        {
            "transaction_id": result["transaction_id"],
            "external_transaction_id": f"{result['external_transaction_id']}-refund",
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
