from __future__ import annotations

import base64
import hashlib

from treps.hash import verify_return_url_hash

SECRET_KEY = "test-3d-security-key"


def _base_payload() -> dict[str, object]:
    return {
        "threeD_status": "SUCCESS",
        "oid": "ORD-2-s5R6Bm",
        "payment_id": "PAY-2-o5MKk8e",
        "transaction_id": "TRX-2-n4T1Fti5DE",
        "amount": "301.77",
        "currency": "TRY",
        "installment": "1",
    }


def _compute_hash(payload: dict[str, object], secret_key: str) -> str:
    """Independently re-implements the algorithm to compute a valid hash for test fixtures."""
    excluded = {"hash", "encoding", "countdown"}
    keys = sorted(
        (k for k in payload if k.lower() not in excluded and payload[k] is not None and payload[k] != ""),
        key=str.lower,
    )

    def escape(value: object) -> str:
        text = "" if value is None else str(value)
        return text.replace("\\", "\\\\").replace("|", "\\|")

    input_str = "|".join(escape(payload[k]) for k in keys) + "|" + escape(secret_key)
    return base64.b64encode(hashlib.sha512(input_str.encode("utf-8")).digest()).decode("ascii")


def test_returns_true_for_correctly_computed_hash() -> None:
    payload = _base_payload()
    computed = _compute_hash(payload, SECRET_KEY)
    payload["hash"] = computed

    assert verify_return_url_hash(payload, SECRET_KEY) is True


def test_returns_false_when_field_value_is_tampered() -> None:
    payload = _base_payload()
    computed = _compute_hash(payload, SECRET_KEY)
    tampered = {**payload, "amount": "999.99", "hash": computed}

    assert verify_return_url_hash(tampered, SECRET_KEY) is False


def test_returns_false_when_secret_key_is_wrong() -> None:
    payload = _base_payload()
    computed = _compute_hash(payload, SECRET_KEY)
    payload["hash"] = computed

    assert verify_return_url_hash(payload, "wrong-secret") is False


def test_returns_false_when_hash_is_missing_or_empty() -> None:
    with_empty_hash = {**_base_payload(), "hash": ""}
    assert verify_return_url_hash(with_empty_hash, SECRET_KEY) is False
    assert verify_return_url_hash(_base_payload(), SECRET_KEY) is False


def test_ignores_hash_encoding_and_countdown_fields() -> None:
    payload = _base_payload()
    computed = _compute_hash(payload, SECRET_KEY)
    payload = {**payload, "hash": computed, "encoding": "utf-8", "countdown": "30"}

    assert verify_return_url_hash(payload, SECRET_KEY) is True


def test_ignores_fields_with_empty_string_values() -> None:
    with_empty = {**_base_payload(), "external_transaction_id": ""}
    computed = _compute_hash(with_empty, SECRET_KEY)
    payload = {**with_empty, "hash": computed}

    assert verify_return_url_hash(payload, SECRET_KEY) is True

    mutated = {**payload, "external_transaction_id": "now-not-empty"}
    assert verify_return_url_hash(mutated, SECRET_KEY) is False


def test_escapes_backslash_and_pipe_characters_in_values() -> None:
    payload = {**_base_payload(), "return_url": "https://example.com/cb?a=1|2&b=x\\y"}
    computed = _compute_hash(payload, SECRET_KEY)
    payload["hash"] = computed

    assert verify_return_url_hash(payload, SECRET_KEY) is True
