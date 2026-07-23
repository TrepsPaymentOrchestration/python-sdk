"""Verifies the ``hash`` field on a payload posted to your ``return_url`` (by either the 3D
Secure or Hosted Page flow), proving it was not tampered with in transit.

Algorithm (must match byte-for-byte, ported from the documented reference implementation):
1. Drop ``hash``, ``encoding``, ``countdown``, and any field with an empty value.
2. Sort the remaining keys alphabetically, case-insensitive.
3. Escape each value: ``\\`` -> ``\\\\``, ``|`` -> ``\\|`` (same escaping applied to the secret key).
4. Join the escaped values with ``|``, then append the escaped secret key.
5. SHA-512 the resulting string and Base64-encode the digest.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
from collections.abc import Mapping

_ALWAYS_EXCLUDED = {"hash", "encoding", "countdown"}


def _escape_hash_value(value: object) -> str:
    text = "" if value is None else str(value)
    return text.replace("\\", "\\\\").replace("|", "\\|")


def verify_return_url_hash(payload: Mapping[str, object], secret_key: str) -> bool:
    """Verifies a return_url payload against your 3D Security Key.

    Args:
        payload: The raw fields exactly as received on your return_url endpoint — do not
            rename or remap keys/values before calling this.
        secret_key: Your 3D Security Key, from the Treps Portal (Settings).

    Returns:
        True if the computed hash matches ``payload["hash"]``.

    Never trust ``threeD_status == "SUCCESS"`` without this check passing.
    """
    provided_hash = payload.get("hash")
    if not isinstance(provided_hash, str) or provided_hash == "":
        return False

    sorted_keys = sorted(
        (
            key
            for key in payload
            if key.lower() not in _ALWAYS_EXCLUDED and payload[key] is not None and payload[key] != ""
        ),
        key=str.lower,
    )

    hash_input = (
        "|".join(_escape_hash_value(payload[key]) for key in sorted_keys) + "|" + _escape_hash_value(secret_key)
    )

    digest = hashlib.sha512(hash_input.encode("utf-8")).digest()
    calculated_hash = base64.b64encode(digest).decode("ascii")

    return hmac.compare_digest(calculated_hash, provided_hash)
