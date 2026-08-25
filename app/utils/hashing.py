from __future__ import annotations

import hashlib
import json
from typing import Any


def generate_hash(
    value: str,
    algorithm: str = "sha256",
) -> str:
    """
    Generate a cryptographic hash for a string.
    """

    try:
        hasher = hashlib.new(algorithm)
    except ValueError as exc:
        raise ValueError(
            f"Unsupported hashing algorithm: {algorithm}"
        ) from exc

    hasher.update(value.encode("utf-8"))

    return hasher.hexdigest()


def hash_text(value: str) -> str:
    """
    Generate SHA-256 hash for text.
    """

    return generate_hash(value, "sha256")


def generate_claim_hash(claim: dict[str, Any]) -> str:
    """
    Generate a deterministic fingerprint for a claim.

    Useful for duplicate-claim detection.
    """

    normalized_claim = json.dumps(
        claim,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )

    return hash_text(normalized_claim)


def generate_document_hash(content: bytes) -> str:
    """
    Generate SHA-256 hash for document content.
    """

    return hashlib.sha256(content).hexdigest()