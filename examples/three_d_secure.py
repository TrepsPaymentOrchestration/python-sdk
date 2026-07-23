"""Run with: TREPS_USERNAME=... TREPS_PASSWORD=... TREPS_MERCHANT_ID=... python examples/three_d_secure.py

Demonstrates the full 3D Secure flow:
  1. init()                 — start the challenge against the sandbox environment
  2. decode redirect_content — see the HTML form you'd render to send the browser to the bank
  3. handle_return_url()    — how to verify + finalize the callback your server receives afterwards

Step 3 doesn't require a live redirect to demonstrate — it's shown here against a
locally-crafted example payload so you can see verify_return_url_hash succeed/fail without
needing a browser or a running server.
"""

from __future__ import annotations

import base64
import hashlib
import os
import sys
import time

from treps import TrepsApiError, TrepsClient, TrepsEnvironment, verify_return_url_hash

treps = TrepsClient(
    username=os.environ.get("TREPS_USERNAME", ""),
    password=os.environ.get("TREPS_PASSWORD", ""),
    merchant_id=int(os.environ.get("TREPS_MERCHANT_ID", "0")),
    environment=TrepsEnvironment.SANDBOX,
)


def handle_return_url(payload: dict[str, object], three_d_security_key: str) -> None:
    """Your return_url handler. Wire this into whatever framework you use as a POST route —
    the posted form/query fields become `payload` below."""
    if not verify_return_url_hash(payload, three_d_security_key):
        print("Hash verification FAILED — refusing to trust this callback.", file=sys.stderr)
        return

    if payload["threeD_status"] != "SUCCESS":
        print("3D Secure challenge did not succeed:", payload["threeD_status"])
        return

    print("Hash verified, 3D Secure succeeded — finalizing the charge...")

    result = treps.three_d_secure.complete(
        {
            "oid": str(payload["oid"]),
            "payment_id": str(payload["payment_id"]),
            "transaction_id": str(payload["transaction_id"]),
        }
    )
    print("Payment finalized:", result["payment_status_message"])


def main() -> None:
    init = treps.three_d_secure.init(
        {
            "external_order_id": f"example-3ds-{int(time.time() * 1000)}",
            "amount": 100,
            "currency": "TRY",
            "installment": 1,
            "client_ip": "127.0.0.1",
            "return_url": "https://your-site.example.com/payment/return",
            "card": {
                "card_owner_name": "Mehmet Yılmaz",
                "card_number": "5401341234567891",
                "card_expire_year": "28",
                "card_expire_month": "12",
                "card_cvv": "000",
                "card_owner_customer_id": "CUS_EXAMPLE_3DS",
            },
        }
    )
    print("Order created:", init["oid"], init["external_order_id"])

    form_html = base64.b64decode(init["redirect_content"]).decode("utf-8")
    print("Decoded auto-submit form (render this in the customer's browser):\n", form_html)

    # --- The rest happens after the bank redirects the browser back to your return_url. ---
    # Demonstrated below against a locally-crafted example payload, since we don't have a
    # live browser/bank round-trip in this script.
    three_d_security_key = os.environ.get("TREPS_3D_SECURITY_KEY", "demo-secret-key")
    example_payload: dict[str, object] = {
        "threeD_status": "SUCCESS",
        "oid": init["oid"],
        "payment_id": "PAY-2-example",
        "transaction_id": "TRX-2-example",
        "external_order_id": init["external_order_id"],
        "order_amount": "100.00",
        "amount": "100.00",
        "installment": "1",
        "currency": "TRY",
        "complete_required": "YES",
        "duplicate_request": "NO",
        "payment_status": 4,
        "threeD_secure_type": "FULL",
        "return_url": "https://your-site.example.com/payment/return",
    }

    # In production this hash comes from the bank; here we compute one so the demo is runnable.
    excluded = {"hash", "encoding", "countdown"}
    keys = sorted(
        (k for k in example_payload if k.lower() not in excluded),
        key=str.lower,
    )

    def escape(value: object) -> str:
        text = "" if value is None else str(value)
        return text.replace("\\", "\\\\").replace("|", "\\|")

    hash_input = "|".join(escape(example_payload[k]) for k in keys) + "|" + escape(three_d_security_key)
    demo_hash = base64.b64encode(hashlib.sha512(hash_input.encode("utf-8")).digest()).decode("ascii")

    handle_return_url({**example_payload, "hash": demo_hash}, three_d_security_key)


if __name__ == "__main__":
    try:
        main()
    except TrepsApiError as err:
        print("Treps API error:", err, err.errors, file=sys.stderr)
        sys.exit(1)
