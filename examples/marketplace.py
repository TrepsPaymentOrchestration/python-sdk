"""Run with: TREPS_USERNAME=... TREPS_PASSWORD=... TREPS_MERCHANT_ID=... python examples/marketplace.py

Demonstrates the marketplace (split payment) surface: onboarding a sub-merchant, the
approve -> pay/allocate order lifecycle, settlement reporting, and refunding a split order.
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
    reference_id = f"example-submerchant-{int(time.time() * 1000)}"

    submerchant = treps.marketplace.submerchant_add(
        {
            "reference_id": reference_id,
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
    print("Sub-merchant added:", submerchant["reference_id"], submerchant["sole_prop_flag_desc"])

    found = treps.marketplace.submerchant_find({"reference_id": reference_id})
    print(f"submerchant_find matched: {found['total_count']}")

    # Marketplace-wide setting: require manual approval before payouts. Write-only — there's no
    # read endpoint to fetch the current value back.
    treps.marketplace.config({"payment_transfer_approve_required": 1})
    print("Marketplace config updated (write-only, no read-back)")

    # A typical order lifecycle, assuming `oid` came from a split-payment sale
    # (`treps.payments.sale(..., sub_merchants=[...])`) allocated to this sub-merchant:
    oid = "EXAMPLE-OID-0001"

    treps.marketplace.order_approve(
        [{"oid": oid, "sub_merchant_reference_id": reference_id, "partial_approve": False, "approve_amount": 100.0}]
    )
    print("Order approved")

    allocate_result = treps.marketplace.order_pay_allocate(
        [{"sub_merchant_reference_id": reference_id, "amount": 100.0, "payment_reference_codes": ["PAYOUT-0001"]}]
    )
    # IMPORTANT: pay/allocate is atomic across the whole batch. A row's own item["success"]
    # being True does NOT mean it was applied unless the top-level success is also True.
    if allocate_result["success"]:
        print("Allocation applied:", allocate_result["items"])
    else:
        print("Allocation rolled back entirely:", allocate_result["message"])

    # Settlement reporting
    summary = treps.marketplace.settlement_summary({"sub_merchant_reference_ids": [reference_id]})
    for row in summary["items"]:
        print(row["sub_merchant_reference_id"], "net_balance:", row["net_balance"])

    detail = treps.marketplace.settlement_detail({"sub_merchant_reference_ids": [reference_id]})
    print(f"Settlement detail rows: {detail['total_count']}")

    # Kick off an async export, then poll/download it via client.download_jobs.
    treps.marketplace.settlement_summary_export(
        {"report_name": "example-export", "filter": {"sub_merchant_reference_ids": [reference_id]}}
    )
    jobs = treps.download_jobs.search({"report_type": 1})  # 1 = SubMerchantSettlement
    print(f"Download jobs: {jobs['total_count']}")
    for job in jobs["items"]:
        print(job["id"], job["report_name"], "job_status:", job["job_status"])

    # Once a job's job_status == 2 (Completed):
    # file_bytes = treps.download_jobs.download(job_id)

    # Splitting a refund across sub-merchants uses the regular payments.refund() with
    # `sub_merchants` — note this request-side field is `reference_id` (not
    # `sub_merchant_reference_id`, which is the response-side field name used above):
    # treps.payments.refund(
    #     {
    #         "transaction_id": tx_id,
    #         "external_transaction_id": f"{oid}-refund",
    #         "clientIp": "127.0.0.1",
    #         "sub_merchants": [{"reference_id": reference_id, "refund_amount": 100.0}],
    #     }
    # )


if __name__ == "__main__":
    try:
        main()
    except TrepsApiError as err:
        print("Treps API error:", err, err.errors, file=sys.stderr)
        sys.exit(1)
