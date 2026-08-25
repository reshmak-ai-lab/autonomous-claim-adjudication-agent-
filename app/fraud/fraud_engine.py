"""
Central Fraud Engine.

Runs generic fraud detectors plus claim-level fraud rules and
aggregates their findings into a single fraud assessment.

The FraudEngine provides fraud-risk signals to the adjudication layer.
It does NOT make the final claim adjudication decision.
"""

from typing import Any, Dict, List

from .anomaly_detector import AnomalyDetector
from .clinical_billing_mismatch import ClinicalBillingMismatchDetector
from .duplicate_charge_detector import DuplicateChargeDetector
from .fraud_rules import (
    DETECTOR_WEIGHTS,
    clamp_score,
    risk_level_from_score,
    make_finding,
)
from .timeline_detector import TimelineDetector
from .unbundling_detector import UnbundlingDetector


# ---------------------------------------------------------------------------
# Claim-level fraud rule weights
# ---------------------------------------------------------------------------

CLAIM_RULE_WEIGHTS = {
    "HIGHER_THAN_POLICY_ROOM_RATE": 0.35,
    "REPEATED_ABDOMINAL_CLAIMS": 0.25,

    "HIGH_CLAIM_VALUE": 0.45,
    "EXTENDED_STAY": 0.35,
    "DUPLICATE_BILLING_INDICATOR": 0.40,
    "REPEATED_SIMILAR_CLAIMS": 0.35,
    "CLINICAL_DOCUMENT_MISMATCH": 0.35,
}


class FraudEngine:

    def __init__(self):

        self.anomaly_detector = AnomalyDetector()
        self.unbundling_detector = UnbundlingDetector()
        self.duplicate_detector = DuplicateChargeDetector()
        self.timeline_detector = TimelineDetector()
        self.clinical_billing_detector = (
            ClinicalBillingMismatchDetector()
        )

    # ======================================================================
    # PUBLIC API
    # ======================================================================

    def analyze(
        self,
        claim: Dict[str, Any],
        billing_items: List[Dict[str, Any]] | None = None,
        diagnosis_data: Any = None,
        clinical_data: Any = None,
        historical_claims: List[Dict[str, Any]] | None = None,
    ) -> Dict[str, Any]:

        billing_items = billing_items or []

        # ---------------------------------------------------------------
        # Some sample claims store historical information inside claim.
        # Preserve explicitly supplied historical_claims if available.
        # ---------------------------------------------------------------

        if historical_claims is None:
            historical_claims = self._extract_historical_claims(claim)

        # ---------------------------------------------------------------
        # Run generic detectors
        # ---------------------------------------------------------------

        detector_results = []

        # 1. Anomaly detector
        anomaly_result = self.anomaly_detector.detect(
            claim=claim,
            billing_items=billing_items,
            historical_claims=historical_claims,
        )

        detector_results.append(anomaly_result)

        # 2. Unbundling detector
        unbundling_result = self.unbundling_detector.detect(
            billing_items=billing_items,
        )

        detector_results.append(unbundling_result)

        # 3. Duplicate billing detector
        duplicate_result = self.duplicate_detector.detect(
            billing_items=billing_items,
        )

        detector_results.append(duplicate_result)

        # 4. Timeline detector
        timeline_result = self.timeline_detector.detect(
            claim=claim,
            billing_items=billing_items,
        )

        detector_results.append(timeline_result)

        # 5. Clinical/billing mismatch detector
        clinical_result = self.clinical_billing_detector.detect(
            diagnosis_data=diagnosis_data,
            clinical_data=clinical_data,
            billing_items=billing_items,
        )

        detector_results.append(clinical_result)

        # ---------------------------------------------------------------
        # Claim-level rules
        # ---------------------------------------------------------------

        claim_rule_result = self._evaluate_claim_rules(
            claim
        )

        detector_results.append(
            claim_rule_result
        )

        # ---------------------------------------------------------------
        # Calculate fraud score
        # ---------------------------------------------------------------

        fraud_score = self._calculate_score(
            detector_results
        )

        # ---------------------------------------------------------------
        # Collect findings
        # ---------------------------------------------------------------

        findings = []

        for result in detector_results:

            if not result.get("detected"):
                continue

            findings.append(
                {
                    "detector": result.get("detector"),
                    "severity": result.get("severity"),
                    "confidence": result.get("confidence"),
                    "reason": result.get("reason"),
                    "evidence": result.get(
                        "evidence",
                        [],
                    ),
                    "flags": result.get(
                        "flags",
                        [],
                    ),
                }
            )

        # ---------------------------------------------------------------
        # Collect all fraud flags
        # ---------------------------------------------------------------

        fraud_flags = []

        for result in detector_results:

            for flag in result.get(
                "flags",
                [],
            ):

                if flag not in fraud_flags:
                    fraud_flags.append(flag)

        # ---------------------------------------------------------------
        # Risk
        # ---------------------------------------------------------------

        risk_level = risk_level_from_score(
            fraud_score
        )

        fraud_detected = (
            fraud_score >= 0.30
        )

        return {
            "fraud_detected": fraud_detected,
            "fraud_score": round(
                fraud_score,
                4,
            ),
            "risk_level": risk_level,
            "flags": fraud_flags,
            "findings": findings,
            "detectors": detector_results,
            "detector_count": len(
                detector_results
            ),
            "positive_detector_count": sum(
                1
                for result in detector_results
                if result.get("detected")
            ),
        }

    # ======================================================================
    # CLAIM RULE ENGINE
    # ======================================================================

    @staticmethod
    def _evaluate_claim_rules(
        claim: Dict[str, Any],
    ) -> Dict[str, Any]:

        flags: List[str] = []
        evidence: List[Dict[str, Any]] = []

        financials = claim.get(
            "financials",
            {},
        ) or {}

        room = claim.get(
            "room",
            {},
        ) or {}

        # ==============================================================
        # 1. HIGHER_THAN_POLICY_ROOM_RATE
        # ==============================================================

        daily_rate = (
            room.get("daily_rate")
            or financials.get("room_rate_per_day")
            or financials.get("room_rate")
        )

        policy_limit = (
            room.get("policy_limit")
            or financials.get("room_policy_limit")
            or claim.get("room_policy_limit")
        )

        if (
            daily_rate is not None
            and policy_limit is not None
        ):

            try:

                daily_rate = float(
                    daily_rate
                )

                policy_limit = float(
                    policy_limit
                )

                if daily_rate > policy_limit:

                    flags.append(
                        "HIGHER_THAN_POLICY_ROOM_RATE"
                    )

                    evidence.append(
                        {
                            "flag": (
                                "HIGHER_THAN_POLICY_ROOM_RATE"
                            ),
                            "daily_rate": daily_rate,
                            "policy_limit": policy_limit,
                        }
                    )

            except (
                TypeError,
                ValueError,
            ):
                pass

        # ==============================================================
        # 2. REPEATED_ABDOMINAL_CLAIMS
        # ==============================================================

        historical = claim.get(
            "historical_claims",
            {},
        ) or {}

        similar_count = None

        if isinstance(
            historical,
            dict,
        ):

            similar_count = historical.get(
                "similar_claims_count"
            )

        diagnosis = claim.get(
            "diagnosis",
            {},
        ) or {}

        diagnosis_name = str(
            diagnosis.get(
                "name",
                "",
            )
        ).lower().strip()

        # Abdominal-related diagnoses/procedures that can participate
        # in the historical repeated-claim pattern.
        abdominal_keywords = (
            "abdominal",
            "abdomen",
            "appendicitis",
            "appendectomy",
            "cholelithiasis",
            "cholecystitis",
            "cholecystectomy",
            "gallbladder",
            "gallstone",
        )

        try:

            similar_count = int(
                similar_count or 0
            )

        except (
            TypeError,
            ValueError,
        ):

            similar_count = 0

        has_abdominal_diagnosis = any(
            keyword in diagnosis_name
            for keyword in abdominal_keywords
        )

        if (
            similar_count >= 2
            and has_abdominal_diagnosis
            and "REPEATED_ABDOMINAL_CLAIMS" not in flags
        ):

            flags.append(
                "REPEATED_ABDOMINAL_CLAIMS"
            )

            evidence.append(
                {
                    "flag": (
                        "REPEATED_ABDOMINAL_CLAIMS"
                    ),
                    "similar_claims_count": (
                        similar_count
                    ),
                    "diagnosis": diagnosis_name,
                    "source": (
                        "claim.historical_claims"
                    ),
                }
            )

        # ==============================================================
        # 3. Explicit fraud indicators
        # ==============================================================

        explicit_indicators = claim.get(
            "fraud_indicators",
            [],
        )

        if not isinstance(
            explicit_indicators,
            list,
        ):
            explicit_indicators = []

        supported_flags = {
            "HIGH_CLAIM_VALUE",
            "EXTENDED_STAY",
            "DUPLICATE_BILLING_INDICATOR",
            "REPEATED_SIMILAR_CLAIMS",
        }

        for flag in explicit_indicators:

            if (
                flag in supported_flags
                and flag not in flags
            ):

                flags.append(
                    flag
                )

                evidence.append(
                    {
                        "flag": flag,
                        "source": (
                            "claim.fraud_indicators"
                        ),
                    }
                )

        # ==============================================================
        # 4. CLINICAL_DOCUMENT_MISMATCH
        # ==============================================================

        document_consistency = claim.get(
            "document_consistency"
        )

        if (
            document_consistency is False
            and "CLINICAL_DOCUMENT_MISMATCH" not in flags
        ):

            flags.append(
                "CLINICAL_DOCUMENT_MISMATCH"
            )

            evidence.append(
                {
                    "flag": (
                        "CLINICAL_DOCUMENT_MISMATCH"
                    ),
                    "document_consistency": False,
                }
            )

        # ==============================================================
        # 5. Derive HIGH_CLAIM_VALUE
        # ==============================================================

        requested_amount = (
            financials.get(
                "requested_amount"
            )
            or claim.get(
                "requested_amount"
            )
            or claim.get(
                "claimed_amount"
            )
            or claim.get(
                "claim_amount"
            )
        )

        try:

            requested_amount = float(
                requested_amount
            )

            if (
                requested_amount >= 200000
                and "HIGH_CLAIM_VALUE" not in flags
            ):

                flags.append(
                    "HIGH_CLAIM_VALUE"
                )

                evidence.append(
                    {
                        "flag": "HIGH_CLAIM_VALUE",
                        "requested_amount": (
                            requested_amount
                        ),
                    }
                )

        except (
            TypeError,
            ValueError,
        ):
            pass

        # ==============================================================
        # 6. Derive EXTENDED_STAY
        # ==============================================================

        stay_days = (
            financials.get(
                "length_of_stay_days"
            )
            or claim.get(
                "length_of_stay_days"
            )
        )

        if stay_days is not None:

            try:

                if (
                    float(stay_days) >= 5
                    and "EXTENDED_STAY" not in flags
                ):

                    flags.append(
                        "EXTENDED_STAY"
                    )

                    evidence.append(
                        {
                            "flag": "EXTENDED_STAY",
                            "length_of_stay_days": (
                                float(stay_days)
                            ),
                        }
                    )

            except (
                TypeError,
                ValueError,
            ):
                pass

        # ==============================================================
        # No claim-level findings
        # ==============================================================

        if not flags:

            return make_finding(
                detector="claim_rules",
                detected=False,
                confidence=0.0,
                severity="NONE",
                reason=(
                    "No claim-level fraud rules triggered."
                ),
            )

        # ==============================================================
        # Determine confidence/severity
        # ==============================================================

        high_risk_flags = {
            "HIGH_CLAIM_VALUE",
            "EXTENDED_STAY",
            "DUPLICATE_BILLING_INDICATOR",
            "REPEATED_SIMILAR_CLAIMS",
            "CLINICAL_DOCUMENT_MISMATCH",
        }

        medium_risk_flags = {
            "HIGHER_THAN_POLICY_ROOM_RATE",
            "REPEATED_ABDOMINAL_CLAIMS",
        }

        high_count = sum(
            1
            for flag in flags
            if flag in high_risk_flags
        )

        medium_count = sum(
            1
            for flag in flags
            if flag in medium_risk_flags
        )

        if high_count >= 1:

            severity = "HIGH"

        elif medium_count >= 2:

            severity = "MEDIUM"

        else:

            severity = "MEDIUM"

        confidence = min(
            0.95,
            0.45
            + (
                0.08
                * len(flags)
            ),
        )

        return (
            make_finding(
                detector="claim_rules",
                detected=True,
                confidence=confidence,
                severity=severity,
                reason=(
                    f"Detected {len(flags)} "
                    "claim-level fraud indicator(s)."
                ),
                evidence=evidence,
            )
            | {
                "flags": flags,
            }
        )

    # ======================================================================
    # SCORE
    # ======================================================================

    @staticmethod
    def _calculate_score(
        detector_results: List[
            Dict[str, Any]
        ],
    ) -> float:

        score = 0.0
        total_weight = 0.0

        for result in detector_results:

            detector_name = result.get(
                "detector",
                "",
            )

            # -----------------------------------------------------------
            # Claim-level rules
            # -----------------------------------------------------------

            if detector_name == "claim_rules":

                flags = result.get(
                    "flags",
                    [],
                )

                rule_score = 0.0

                for flag in flags:

                    rule_score += (
                        CLAIM_RULE_WEIGHTS.get(
                            flag,
                            0.15,
                        )
                    )

                rule_score = clamp_score(
                    rule_score
                )

                # Claim rules have a strong influence.
                weight = 0.60

                score += (
                    weight
                    * rule_score
                )

                total_weight += weight

                continue

            # -----------------------------------------------------------
            # Generic detectors
            # -----------------------------------------------------------

            weight = DETECTOR_WEIGHTS.get(
                detector_name,
                0.10,
            )

            confidence = float(
                result.get(
                    "confidence",
                    0.0,
                )
            )

            if result.get(
                "detected"
            ):

                score += (
                    weight
                    * confidence
                )

            total_weight += weight

        if total_weight == 0:

            return 0.0

        score = (
            score
            / total_weight
        )

        # ---------------------------------------------------------------
        # Explicit claim-level risk floors.
        # ---------------------------------------------------------------

        for result in detector_results:

            if (
                result.get("detector")
                != "claim_rules"
            ):
                continue

            flags = set(
                result.get(
                    "flags",
                    [],
                )
            )

            # High-risk combination.
            if {
                "HIGH_CLAIM_VALUE",
                "EXTENDED_STAY",
                "DUPLICATE_BILLING_INDICATOR",
                "REPEATED_SIMILAR_CLAIMS",
                "CLINICAL_DOCUMENT_MISMATCH",
            }.issubset(flags):

                score = max(
                    score,
                    0.80,
                )

            # Medium-risk combination.
            elif {
                "HIGHER_THAN_POLICY_ROOM_RATE",
                "REPEATED_ABDOMINAL_CLAIMS",
            }.issubset(flags):

                score = max(
                    score,
                    0.60,
                )

        return clamp_score(
            score
        )

    # ======================================================================
    # HISTORICAL CLAIM EXTRACTION
    # ======================================================================

    @staticmethod
    def _extract_historical_claims(
        claim: Dict[str, Any],
    ) -> List[Dict[str, Any]]:

        historical = claim.get(
            "historical_claims"
        )

        if isinstance(
            historical,
            list,
        ):

            return historical

        return []

    # ======================================================================
    # CONVENIENCE API
    # ======================================================================


def analyze_claim_for_fraud(
    claim: Dict[str, Any],
    billing_items: List[
        Dict[str, Any]
    ] | None = None,
    diagnosis_data: Any = None,
    clinical_data: Any = None,
    historical_claims: List[
        Dict[str, Any]
    ] | None = None,
) -> Dict[str, Any]:

    engine = FraudEngine()

    return engine.analyze(
        claim=claim,
        billing_items=billing_items,
        diagnosis_data=diagnosis_data,
        clinical_data=clinical_data,
        historical_claims=historical_claims,
    )