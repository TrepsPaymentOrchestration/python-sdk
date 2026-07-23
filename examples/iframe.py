"""Run with: TREPS_USERNAME=... TREPS_PASSWORD=... TREPS_MERCHANT_ID=... python examples/iframe.py

Demonstrates the embedded IFrame checkout — the same /api/payment/hostedpage endpoint as the
Secure Payment Page, but with iframe_flag: 1 and styling via 'css-variables'.
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
    session = treps.hosted_page.create_iframe(
        {
            "external_order_id": f"example-iframe-{int(time.time() * 1000)}",
            "amount": 2500,
            "currency": "TRY",
            "transaction_type": 1,
            "return_url": "https://example.com/payment/return",
            "iframe_web_uri": "https://example.com/checkout",
            "lang": "tr",
            "css-variables": {
                "text-color": "#1f2937",
                "font-family": "Segoe UI, Roboto, sans-serif",
                "font-size": "16px",
                "button-background-color": "#10b981",
                "button-background-color-hover": "#059669",
                "hide-installments": "0",
                "hide-pay-button": "0",
            },
        }
    )

    print('Embed this in an <iframe src="...">:', session["url"])
    print("Session token (for polling):", session["token"])

    # query() works the same way for both create_iframe() and create() (Hosted Page) sessions.
    status = treps.hosted_page.query(session["token"])
    print("Order completed?", status["order"]["order_completed"])


if __name__ == "__main__":
    try:
        main()
    except TrepsApiError as err:
        print("Treps API error:", err, err.errors, file=sys.stderr)
        sys.exit(1)
