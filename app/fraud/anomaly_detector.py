"""
Billing anomaly detector.

Detects unusually high claim amounts and unusually high procedure
amounts based on available historical/reference information.
"""

from typing import Any 

from .fraud_rules import ANOMALY_RULES, make_finding


class AnomalyDetector:

    def detect(
        self,
        claim: dict[str, Any],
        billing_items: list[dict[str, Any]],
        historical_claims: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:

        findings = []

        claim_amount = float(
            claim.get("claimed_amount")
            or claim.get("claim_amount")
            or claim.get("total_amount")
            or 0
        )

        if claim_amount >= ANOMALY_RULES["very_high_amount"]:
            findings.append(
                {
                    "type": "very_high_claim_amount",
                    "amount": claim_amount,
                    "reason": (
                        f"Claim amount {claim_amount:.2f} exceeds the "
                        "very-high amount threshold."
                    ),
                }
            )

        elif claim_amount >= ANOMALY_RULES["high_amount"]:
            findings.append(
                {
                    "type": "high_claim_amount",
                    "amount": claim_amount,
                    "reason": (
                        f"Claim amount {claim_amount:.2f} exceeds the "
                        "high amount threshold."
                    ),
                }
            )

        # ------------------------------------------------------------------
        # Compare against historical claims when available.
        # ------------------------------------------------------------------

        if historical_claims:

            historical_amounts = []

            for historical in historical_claims:
                amount = (
                    historical.get("claimed_amount")
                    or historical.get("claim_amount")
                    or historical.get("total_amount")
                )

                if amount is not None:
                    try:
                        historical_amounts.append(float(amount))
                    except (TypeError, ValueError):
                        continue

            if historical_amounts:

                average_amount = sum(historical_amounts) / len(
                    historical_amounts
                )

                if (
                    average_amount > 0
                    and claim_amount
                    >= average_amount * ANOMALY_RULES["amount_multiplier"]
                ):
                    findings.append(
                        {
                            "type": "historical_amount_anomaly",
                            "claim_amount": claim_amount,
                            "historical_average": average_amount,
                            "reason": (
                                "Claim amount is significantly higher than "
                                "the historical average."
                            ),
                        }
                    )

        # ------------------------------------------------------------------
        # Analyze individual billing items.
        # ------------------------------------------------------------------

        for item in billing_items:

            amount = item.get("amount", 0)

            try:
                amount = float(amount)
            except (TypeError, ValueError):
                continue

            if amount >= ANOMALY_RULES["very_high_amount"]:
                findings.append(
                    {
                        "type": "very_high_billing_item",
                        "amount": amount,
                        "procedure": (
                            item.get("procedure_name")
                            or item.get("description")
                        ),
                        "reason": "Individual billing item has an unusually high amount.",
                    }
                )

        if not findings:
            return make_finding(
                detector="anomaly",
                detected=False,
                confidence=0.05,
                severity="NONE",
                reason="No significant billing anomalies detected.",
            )

        confidence = min(
            0.95,
            0.55 + (0.08 * len(findings)),
        )

        severity = "HIGH" if claim_amount >= ANOMALY_RULES[
            "very_high_amount"
        ] else "MEDIUM"

        return make_finding(
            detector="anomaly",
            detected=True,
            confidence=confidence,
            severity=severity,
            reason=f"Detected {len(findings)} billing anomaly/anomalies.",
            evidence=findings,
        )


def detect_anomalies(
    claim: dict[str, Any],
    billing_items: list[dict[str, Any]],
    historical_claims: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:

    return AnomalyDetector().detect(
        claim,
        billing_items,
        historical_claims,
    )