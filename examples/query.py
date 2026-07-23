"""Run with: TREPS_USERNAME=... TREPS_PASSWORD=... TREPS_MERCHANT_ID=... python examples/query.py

Demonstrates the read-only query/reporting operations: BIN lookup, transaction and order
detail, paginated reports, commission schemes, installment options, and saved-card search.
"""

from __future__ import annotations

import os
import sys

from treps import TrepsApiError, TrepsClient, TrepsEnvironment

treps = TrepsClient(
    username=os.environ.get("TREPS_USERNAME", ""),
    password=os.environ.get("TREPS_PASSWORD", ""),
    merchant_id=int(os.environ.get("TREPS_MERCHANT_ID", "0")),
    environment=TrepsEnvironment.SANDBOX,
)


def main() -> None:
    bin_info = treps.query.bin({"card_bin": "43550843"})
    print("BIN lookup:", bin_info["card_brand"], bin_info["card_network"], bin_info["card_country"])

    report = treps.query.transaction_report({"page": 1, "page_size": 10})
    print(f"Transaction report: {len(report)} transaction(s) on this page")

    if report:
        detail = treps.query.transaction_detail({"transaction_id": report[0]["transaction_id"]})
        print("Transaction detail:", detail["transaction_id"], detail["result_message"] or detail["transaction_status"])

    orders = treps.query.order_report({"page": 1, "page_size": 10})
    print(f"Order report: {orders['total_count']} order(s) total")

    if orders["data"]:
        order_detail = treps.query.order_detail({"external_order_id": orders["data"][0]["external_order_id"]})
        print("Order detail products:", [p["name"] for p in order_detail["order"]["products"]])

    schemes = treps.query.customer_commissions()
    print(f"Commission schemes: {len(schemes)}")

    if schemes:
        items = treps.query.customer_commission_items(schemes[0]["code"])
        print("Commission items for", schemes[0]["code"], ":", len(items["items"]))

    installments = treps.query.installments({"bin": "48248929", "amount": 100, "currency": "TRY", "planCode": "Mus_01"})
    print("Installment options:", installments["installments"])

    cards = treps.query.cards({"customer_code": "CARD10"})
    print(f"Saved cards for CARD10: {len(cards['cards'])}")


if __name__ == "__main__":
    try:
        main()
    except TrepsApiError as err:
        print("Treps API error:", err, err.errors, file=sys.stderr)
        sys.exit(1)
