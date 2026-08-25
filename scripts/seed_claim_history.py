"""
Seed historical claim data into the claim-history memory.

Usage:
    python scripts/seed_claim_history.py

The script reads sample claims from:

    data/sample_claims/

and stores useful historical information through the project's
claim history service.
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List


# ---------------------------------------------------------------------
# Project root
# ---------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ---------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(
    "seed_claim_history"
)


# ---------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------

SAMPLE_CLAIMS_DIR = (
    PROJECT_ROOT
    / "data"
    / "sample_claims"
)


# ---------------------------------------------------------------------
# Claim loading
# ---------------------------------------------------------------------

def load_claim_files() -> List[Dict[str, Any]]:
    """
    Load all JSON claim files from data/sample_claims.
    """

    claims: List[Dict[str, Any]] = []

    if not SAMPLE_CLAIMS_DIR.exists():

        raise FileNotFoundError(
            f"Claim directory not found: "
            f"{SAMPLE_CLAIMS_DIR}"
        )

    json_files = sorted(
        SAMPLE_CLAIMS_DIR.rglob("*.json")
    )

    if not json_files:

        logger.warning(
            "No claim JSON files found in %s",
            SAMPLE_CLAIMS_DIR,
        )

        return claims

    for file_path in json_files:

        try:

            with file_path.open(
                "r",
                encoding="utf-8",
            ) as file:

                data = json.load(file)

            if isinstance(data, dict):

                data["_source_file"] = str(
                    file_path.relative_to(
                        PROJECT_ROOT
                    )
                )

                claims.append(data)

                logger.info(
                    "Loaded claim: %s",
                    data.get(
                        "claim_id",
                        file_path.name,
                    ),
                )

            elif isinstance(data, list):

                for item in data:

                    if isinstance(item, dict):

                        item["_source_file"] = str(
                            file_path.relative_to(
                                PROJECT_ROOT
                            )
                        )

                        claims.append(item)

                logger.info(
                    "Loaded %d claims from %s",
                    len(data),
                    file_path.name,
                )

        except json.JSONDecodeError as exc:

            logger.error(
                "Invalid JSON in %s: %s",
                file_path,
                exc,
            )

        except OSError as exc:

            logger.error(
                "Could not read %s: %s",
                file_path,
                exc,
            )

    return claims


# ---------------------------------------------------------------------
# Claim normalization
# ---------------------------------------------------------------------

def normalize_claim(
    claim: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Convert a raw claim into a compact historical record.

    This keeps only information useful for claim-history retrieval.
    """

    claim_id = claim.get(
        "claim_id",
        "UNKNOWN",
    )

    patient_id = claim.get(
        "patient_id"
    )

    policy_id = claim.get(
        "policy_id"
    )

    hospital_id = claim.get(
        "hospital_id"
    )

    decision = (
        claim.get("decision")
        or claim.get("status")
        or claim.get("claim_status")
    )

    claimed_amount = claim.get(
        "claimed_amount",
        claim.get("claim_amount", 0),
    )

    payable_amount = claim.get(
        "payable_amount",
        claim.get("approved_amount", 0),
    )

    return {
        "claim_id": claim_id,
        "patient_id": patient_id,
        "policy_id": policy_id,
        "hospital_id": hospital_id,
        "decision": decision,
        "claimed_amount": claimed_amount,
        "payable_amount": payable_amount,
        "diagnosis": claim.get(
            "diagnosis"
        ),
        "procedure": claim.get(
            "procedure"
        ),
        "admission_date": claim.get(
            "admission_date"
        ),
        "discharge_date": claim.get(
            "discharge_date"
        ),
        "fraud_flag": claim.get(
            "fraud_flag",
            False,
        ),
        "source_file": claim.get(
            "_source_file"
        ),
    }


# ---------------------------------------------------------------------
# Memory payload
# ---------------------------------------------------------------------

def build_memory_text(
    claim: Dict[str, Any],
) -> str:
    """
    Convert a historical claim into text suitable for Mem0
    or another semantic memory store.
    """

    return (
        f"Historical insurance claim {claim['claim_id']}. "
        f"Patient: {claim.get('patient_id')}. "
        f"Policy: {claim.get('policy_id')}. "
        f"Hospital: {claim.get('hospital_id')}. "
        f"Diagnosis: {claim.get('diagnosis')}. "
        f"Procedure: {claim.get('procedure')}. "
        f"Claimed amount: {claim.get('claimed_amount')}. "
        f"Payable amount: {claim.get('payable_amount')}. "
        f"Decision: {claim.get('decision')}. "
        f"Fraud flag: {claim.get('fraud_flag')}."
    )


# ---------------------------------------------------------------------
# Claim-history service
# ---------------------------------------------------------------------

def get_claim_history_service():
    """
    Create the project's claim-history service.

    The import is kept here so the script can be adjusted easily
    if your existing claim_history.py uses a different class name.
    """

    try:

        from app.memory.claim_history import (
            ClaimHistory,
        )

        return ClaimHistory()

    except ImportError as exc:

        raise ImportError(
            "Could not import ClaimHistory from "
            "app.memory.claim_history. "
            "Check that claim_history.py contains "
            "a ClaimHistory class."
        ) from exc


# ---------------------------------------------------------------------
# Store claim
# ---------------------------------------------------------------------

def store_claim(
    service: Any,
    claim: Dict[str, Any],
) -> bool:
    """
    Store one historical claim.

    Supports a few common method names so it can work with
    different implementations of ClaimHistory.
    """

    memory_text = build_memory_text(
        claim
    )

    metadata = {
        "claim_id": claim["claim_id"],
        "patient_id": claim.get(
            "patient_id"
        ),
        "policy_id": claim.get(
            "policy_id"
        ),
        "hospital_id": claim.get(
            "hospital_id"
        ),
        "decision": claim.get(
            "decision"
        ),
        "claimed_amount": claim.get(
            "claimed_amount"
        ),
        "payable_amount": claim.get(
            "payable_amount"
        ),
        "fraud_flag": claim.get(
            "fraud_flag"
        ),
    }

    # Preferred interface.
    if hasattr(service, "store_claim"):

        service.store_claim(
            claim_id=claim["claim_id"],
            claim=claim,
            memory_text=memory_text,
            metadata=metadata,
        )

        return True

    # Alternative interface.
    if hasattr(service, "add_claim"):

        service.add_claim(
            claim_id=claim["claim_id"],
            claim=claim,
            metadata=metadata,
        )

        return True

    # Alternative Mem0-style interface.
    if hasattr(service, "add"):

        service.add(
            memory_text,
            metadata=metadata,
        )

        return True

    raise AttributeError(
        "ClaimHistory service does not expose "
        "store_claim(), add_claim(), or add()."
    )


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main() -> None:

    logger.info(
        "=" * 70
    )

    logger.info(
        "CLAIM HISTORY SEEDING"
    )

    logger.info(
        "=" * 70
    )

    # 1. Load sample claims.
    raw_claims = load_claim_files()

    if not raw_claims:

        logger.warning(
            "No claims available for seeding."
        )

        return

    logger.info(
        "Total claims loaded: %d",
        len(raw_claims),
    )

    # 2. Normalize claims.
    claims = [
        normalize_claim(claim)
        for claim in raw_claims
    ]

    # 3. Create memory service.
    service = get_claim_history_service()

    # 4. Store each claim.
    success_count = 0
    failure_count = 0

    for claim in claims:

        claim_id = claim["claim_id"]

        try:

            stored = store_claim(
                service,
                claim,
            )

            if stored:

                success_count += 1

                logger.info(
                    "Seeded claim history: %s",
                    claim_id,
                )

        except Exception as exc:

            failure_count += 1

            logger.exception(
                "Failed to seed claim %s: %s",
                claim_id,
                exc,
            )

    # 5. Summary.
    logger.info(
        "=" * 70
    )

    logger.info(
        "SEEDING COMPLETE"
    )

    logger.info(
        "Loaded: %d",
        len(claims),
    )

    logger.info(
        "Successfully seeded: %d",
        success_count,
    )

    logger.info(
        "Failed: %d",
        failure_count,
    )

    logger.info(
        "=" * 70
    )


if __name__ == "__main__":
    main()