"""Run with: TREPS_USERNAME=... TREPS_PASSWORD=... TREPS_MERCHANT_ID=... python examples/card.py

Demonstrates saved/tokenized card management: add, update, remove, and (via the query
resource) search.
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
    customer_code = f"example-customer-{int(time.time() * 1000)}"

    added = treps.cards.add(
        {
            "card_owner_name": "Mehmet Yılmaz",
            "customer_code": customer_code,
            "card_number": "5406675406675403",
            "card_expire_date": "12/2040",
            "card_alias": "İş Bankası kartım",
            "card_reference_code": f"ref-{int(time.time() * 1000)}",
        }
    )
    print("Card added, token:", added["card_token"])

    treps.cards.update(
        {
            "customer_code": customer_code,
            "card_token": added["card_token"],
            "card_alias": "Yeni takma ad",
            "card_owner_name": "Mehmet Yılmaz",
            "card_expire_date": "12/2040",
        }
    )
    print("Card alias updated")

    found = treps.query.cards({"customer_code": customer_code})
    print(f"Cards for {customer_code}:", len(found["cards"]))

    removed = treps.cards.remove({"customer_code": customer_code, "card_token": added["card_token"]})
    print("Card removed:", removed["removed"])


if __name__ == "__main__":
    try:
        main()
    except TrepsApiError as err:
        print("Treps API error:", err, err.errors, file=sys.stderr)
        sys.exit(1)
