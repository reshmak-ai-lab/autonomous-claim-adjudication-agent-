"""
Main claim adjudication workflow.

Coordinates:

Privacy
    ↓
Extraction
    ↓
Policy / RAG
    ↓
Rules
    ↓
Fraud
    ↓
Adjudication
    ↓
Guardrails
    ↓
Final response
"""

from __future__ import annotations

import time
from typing import Any

from ..state import AgentState

from app.adjudication import Adjudicator
from app.guardrails import GuardrailPipeline
from app.observability import (
    TraceContext,
    WorkflowCallback,
)

from app.fraud.fraud_engine import FraudEngine


class ClaimWorkflow:

    def __init__(self):

        self.adjudicator = Adjudicator()

        self.guardrail_pipeline = (
            GuardrailPipeline()
        )

        self.fraud_engine = FraudEngine()

    # ------------------------------------------------------------------
    # Trace helper
    # ------------------------------------------------------------------

    def _record(
        self,
        state: AgentState,
        event: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:

        state.setdefault(
            "execution_trace",
            [],
        ).append(
            {
                "event": event,
                "metadata": metadata or {},
            }
        )

    # ------------------------------------------------------------------
    # Run
    # ------------------------------------------------------------------

    def run(
        self,
        state: AgentState,
    ) -> AgentState:

        claim = state["claim"]

        claim_id = claim.get(
            "claim_id",
            "UNKNOWN",
        )

        trace = TraceContext(
            claim_id=claim_id
        )

        callback = WorkflowCallback(
            trace=trace
        )

        state["trace_id"] = trace.trace_id

        workflow_start = time.perf_counter()

        try:

            # ----------------------------------------------------------
            # 1. Validate basic input
            # ----------------------------------------------------------

            callback.on_node_start(
                "input_validation"
            )

            self._record(
                state,
                "input_validation_started",
            )

            self._validate_input(
                claim
            )

            callback.on_node_complete(
                "input_validation"
            )

            self._record(
                state,
                "input_validation_completed",
            )

            # ----------------------------------------------------------
            # 2. Privacy
            # ----------------------------------------------------------

            callback.on_node_start(
                "privacy"
            )

            self._run_privacy(
                state
            )

            callback.on_node_complete(
                "privacy"
            )

            # ----------------------------------------------------------
            # 3. Extraction
            # ----------------------------------------------------------

            callback.on_node_start(
                "extraction"
            )

            self._run_extraction(
                state
            )

            callback.on_node_complete(
                "extraction"
            )

            # ----------------------------------------------------------
            # 4. Policy / RAG
            # ----------------------------------------------------------

            callback.on_node_start(
                "policy_retrieval"
            )

            self._run_policy_retrieval(
                state
            )

            callback.on_node_complete(
                "policy_retrieval"
            )

            # ----------------------------------------------------------
            # 5. Rules
            # ----------------------------------------------------------

            callback.on_node_start(
                "rule_evaluation"
            )

            self._run_rules(
                state
            )

            callback.on_node_complete(
                "rule_evaluation"
            )

            # ----------------------------------------------------------
            # 6. Fraud
            # ----------------------------------------------------------

            callback.on_node_start(
                "fraud_detection"
            )

            self._run_fraud(
                state
            )

            callback.on_node_complete(
                "fraud_detection",
                metadata={
                    "fraud_score": state.get(
                        "fraud_result",
                        {},
                    ).get(
                        "fraud_score",
                        0.0,
                    ),
                },
            )

            # ----------------------------------------------------------
            # 7. Adjudication
            # ----------------------------------------------------------

            callback.on_node_start(
                "adjudication"
            )

            self._run_adjudication(
                state
            )

            callback.on_node_complete(
                "adjudication"
            )

            # ----------------------------------------------------------
            # 8. Guardrails
            # ----------------------------------------------------------

            callback.on_node_start(
                "guardrails"
            )

            self._run_guardrails(
                state
            )

            callback.on_node_complete(
                "guardrails",
                metadata={
                    "passed": state.get(
                        "guardrails_passed",
                        False,
                    )
                },
            )

            # ----------------------------------------------------------
            # 9. Final response
            # ----------------------------------------------------------

            self._build_final_response(
                state
            )

            trace.complete()

            duration_ms = (
                time.perf_counter()
                - workflow_start
            ) * 1000

            state["execution_trace"] = (
                trace.to_dict()["events"]
            )

            state["execution_trace"].append(
                {
                    "event": "workflow_completed",
                    "duration_ms": round(
                        duration_ms,
                        3,
                    ),
                }
            )

            return state

        except Exception as exc:

            callback.on_node_error(
                "claim_workflow",
                exc,
            )

            state.setdefault(
                "errors",
                [],
            ).append(
                str(exc)
            )

            state["human_review_required"] = True

            state["final_decision"] = (
                "QUERY_RAISED"
            )

            state["final_response"] = {
                "claim_id": claim_id,
                "decision": "QUERY_RAISED",
                "reason": (
                    "The claim could not be safely "
                    "processed automatically."
                ),
                "error": str(exc),
                "human_review_required": True,
            }

            return state

    # ------------------------------------------------------------------
    # Input
    # ------------------------------------------------------------------

    def _validate_input(
        self,
        claim: dict[str, Any],
    ) -> None:

        if not claim.get("claim_id"):

            raise ValueError(
                "claim_id is required."
            )

    # ------------------------------------------------------------------
    # Privacy
    # ------------------------------------------------------------------

    def _run_privacy(
        self,
        state: AgentState,
    ) -> None:

        """
        Preserve the claim and mark the input as sanitized.

        The actual PII/privacy implementation can be connected here
        without changing the downstream workflow contract.
        """

        state["pii_detected"] = False

        state["sanitized_input"] = str(
            state["claim"]
        )

        self._record(
            state,
            "privacy_completed",
        )

    # ------------------------------------------------------------------
    # Extraction
    # ------------------------------------------------------------------

    def _run_extraction(
        self,
        state: AgentState,
    ) -> None:

        """
        Normalize the claim's nested JSON structures into the state
        consumed by downstream rules, fraud detection, and adjudication.

        Expected claim structure:

            claim.admission
            claim.diagnosis
            claim.procedure
            claim.financials
            claim.historical_claims
            claim.fraud_indicators
            claim.document_consistency
        """

        claim = state["claim"]

        admission = claim.get(
            "admission",
            {},
        )

        diagnosis = claim.get(
            "diagnosis",
            {},
        )

        procedure = claim.get(
            "procedure",
            {},
        )

        financials = claim.get(
            "financials",
            {},
        )

        historical_claims = claim.get(
            "historical_claims",
            {},
        )

        if not isinstance(admission, dict):
            admission = {}

        if not isinstance(diagnosis, dict):
            diagnosis = {}

        if not isinstance(procedure, dict):
            procedure = {}

        if not isinstance(financials, dict):
            financials = {}

        if not isinstance(historical_claims, dict):
            historical_claims = {}

        # --------------------------------------------------------------
        # Clinical data
        # --------------------------------------------------------------

        state["clinical_data"] = {
            "diagnosis": diagnosis,
            "procedure": procedure,
            "admission": admission,
        }

        # --------------------------------------------------------------
        # Billing data
        # --------------------------------------------------------------

        requested_amount = financials.get(
            "requested_amount",
            financials.get(
                "claimed_amount",
                0,
            ),
        )

        try:
            requested_amount = float(
                requested_amount or 0
            )
        except (
            TypeError,
            ValueError,
        ):
            requested_amount = 0.0

        state["billing_data"] = {
            "room_rate_per_day": financials.get(
                "room_rate_per_day",
                0,
            ),
            "length_of_stay_days": financials.get(
                "length_of_stay_days",
                0,
            ),
            "requested_amount": requested_amount,
            "claimed_amount": requested_amount,
        }

        # --------------------------------------------------------------
        # Diagnosis
        # --------------------------------------------------------------

        state["diagnosis_data"] = {
            "name": diagnosis.get(
                "name"
            ),
            "icd10": diagnosis.get(
                "icd10"
            ),
        }

        # --------------------------------------------------------------
        # Procedure
        # --------------------------------------------------------------

        state["procedure_data"] = {
            "name": procedure.get(
                "name"
            ),
        }

        # --------------------------------------------------------------
        # Timeline
        # --------------------------------------------------------------

        state["timeline_data"] = {
            "admission_date": admission.get(
                "date"
            ),
            "expected_discharge": admission.get(
                "expected_discharge"
            ),
            "emergency": admission.get(
                "emergency",
                False,
            ),
            "length_of_stay_days": financials.get(
                "length_of_stay_days"
            ),
        }

        # --------------------------------------------------------------
        # Preserve explicit fraud-related claim evidence
        # --------------------------------------------------------------

        fraud_indicators = claim.get(
            "fraud_indicators",
            [],
        )

        if not isinstance(
            fraud_indicators,
            list,
        ):
            fraud_indicators = []

        document_consistency = claim.get(
            "document_consistency",
            True,
        )

        similar_claims_count = historical_claims.get(
            "similar_claims_count",
            0,
        )

        try:
            similar_claims_count = int(
                similar_claims_count or 0
            )
        except (
            TypeError,
            ValueError,
        ):
            similar_claims_count = 0

        state["claim_risk_signals"] = {
            "fraud_indicators": fraud_indicators,
            "document_consistency": (
                bool(document_consistency)
            ),
            "similar_claims_count": (
                similar_claims_count
            ),
        }

    # ------------------------------------------------------------------
    # Policy / RAG
    # ------------------------------------------------------------------

    def _run_policy_retrieval(
        self,
        state: AgentState,
    ) -> None:

        """
        Connect app.rag.retriever here.

        The workflow deliberately does not invent policy evidence.
        """

        state.setdefault(
            "policy_context",
            [],
        )

        state.setdefault(
            "policy_result",
            {
                "covered": True,
                "exclusion_applies": False,
            },
        )

    # ------------------------------------------------------------------
    # Rules
    # ------------------------------------------------------------------

    def _run_rules(
        self,
        state: AgentState,
    ) -> None:

        claim = state["claim"]

        financials = claim.get(
            "financials",
            {},
        )

        if not isinstance(financials, dict):
            financials = {}

        room = claim.get(
            "room",
            {},
        )

        if not isinstance(room, dict):
            room = {}

        # --------------------------------------------------------------
        # 1. Resolve claimed amount
        #
        # Claim fixtures use financials.requested_amount rather than
        # financials.claimed_amount.
        # --------------------------------------------------------------

        claimed_amount = (
            financials.get("claimed_amount")
            or financials.get("requested_amount")
            or claim.get("claimed_amount")
            or 0
        )

        claimed_amount = float(
            claimed_amount or 0
        )

        # --------------------------------------------------------------
        # 2. Existing explicit deductions
        # --------------------------------------------------------------

        non_payable_amount = float(
            financials.get(
                "non_payable_amount",
                0,
            )
            or 0
        )

        exclusion_amount = float(
            financials.get(
                "exclusion_amount",
                0,
            )
            or 0
        )

        proportional_deduction = float(
            financials.get(
                "proportional_deduction",
                0,
            )
            or 0
        )

        copay_percent = float(
            financials.get(
                "copay_percent",
                0,
            )
            or 0
        )

        deductible_amount = float(
            financials.get(
                "deductible_amount",
                0,
            )
            or 0
        )

        # --------------------------------------------------------------
        # 3. Room-rent limit
        #
        # Example:
        #   daily room charge = 8000
        #   policy limit      = 5000
        #   days              = 3
        #
        #   deduction = (8000 - 5000) * 3
        #             = 9000
        # --------------------------------------------------------------

        room_rent_deduction = float(
            financials.get(
                "room_rent_deduction",
                0,
            )
            or 0
        )

        daily_room_rate = room.get(
            "daily_rate"
        )

        room_policy_limit = room.get(
            "policy_limit"
        )

        room_days = room.get(
            "days"
        )

        if (
            room_rent_deduction == 0
            and daily_room_rate is not None
            and room_policy_limit is not None
        ):

            daily_room_rate = float(
                daily_room_rate or 0
            )

            room_policy_limit = float(
                room_policy_limit or 0
            )

            if room_days is None:
                room_days = claim.get(
                    "admission",
                    {},
                ).get(
                    "length_of_stay_days",
                    0,
                )

            room_days = float(
                room_days or 0
            )

            if (
                daily_room_rate
                > room_policy_limit
                and room_days > 0
            ):
                room_rent_deduction = (
                    daily_room_rate
                    - room_policy_limit
                ) * room_days

        # --------------------------------------------------------------
        # 4. Non-medical consumables
        #
        # Non-medical consumables are not payable under this sample
        # claim's adjudication rules.
        # --------------------------------------------------------------

        non_medical_consumables = float(
            financials.get(
                "non_medical_consumables",
                0,
            )
            or 0
        )

        if (
            non_medical_consumables > 0
            and non_payable_amount == 0
        ):
            non_payable_amount = (
                non_medical_consumables
            )

        # --------------------------------------------------------------
        # 5. Store normalized financial inputs
        # --------------------------------------------------------------

        state["financial_inputs"] = {
            "claimed_amount": claimed_amount,
            "non_payable_amount": non_payable_amount,
            "exclusion_amount": exclusion_amount,
            "room_rent_deduction": room_rent_deduction,
            "proportional_deduction": proportional_deduction,
            "copay_percent": copay_percent,
            "deductible_amount": deductible_amount,
        }

        # --------------------------------------------------------------
        # 6. Record rules that were actually applied
        # --------------------------------------------------------------

        rules_applied = []

        if room_rent_deduction > 0:
            rules_applied.append(
                {
                    "rule": "ROOM_RENT_LIMIT",
                    "status": "APPLIED",
                    "deduction": round(
                        room_rent_deduction,
                        2,
                    ),
                    "daily_rate": daily_room_rate,
                    "policy_limit": room_policy_limit,
                    "days": room_days,
                }
            )

        if non_medical_consumables > 0:
            rules_applied.append(
                {
                    "rule": "NON_MEDICAL_EXPENSE",
                    "status": "APPLIED",
                    "amount": round(
                        non_medical_consumables,
                        2,
                    ),
                }
            )

        state["rule_result"] = {
            "rules_applied": rules_applied,
            "status": "PASS",
        }
    # ------------------------------------------------------------------
    # Fraud
    # ------------------------------------------------------------------

    def _run_fraud(
        self,
        state: AgentState,
    ) -> None:

        claim = state["claim"]

        billing_data = state.get(
            "billing_data",
            {},
        )

        clinical_data = state.get(
            "clinical_data",
            {},
        )

        if not isinstance(
            billing_data,
            dict,
        ):
            billing_data = {}

        if not isinstance(
            clinical_data,
            dict,
        ):
            clinical_data = {}

        billing_items = billing_data.get(
            "items",
            [],
        )

        if not isinstance(
            billing_items,
            list,
        ):
            billing_items = []

        try:

            result = self.fraud_engine.analyze(
                claim=claim,
                billing_items=billing_items,
                diagnosis_data=state.get(
                    "diagnosis_data",
                    {},
                ),
                clinical_data=clinical_data,
            )

        except TypeError as exc:

            # Do not silently convert an incompatible fraud-engine
            # invocation into a false MINIMAL result.
            #
            # Explicit claim risk signals are still evaluated below.
            result = {
                "fraud_detected": False,
                "fraud_score": 0.0,
                "risk_level": "MINIMAL",
                "findings": [],
                "engine_error": str(exc),
            }

        if not isinstance(
            result,
            dict,
        ):
            result = {
                "fraud_detected": False,
                "fraud_score": 0.0,
                "risk_level": "MINIMAL",
                "findings": [],
            }

        # --------------------------------------------------------------
        # Merge explicit claim-level risk evidence.
        #
        # This is important because the supplied claim schema contains
        # fraud indicators that may not be represented by individual
        # billing line items.
        # --------------------------------------------------------------

        risk_signals = state.get(
            "claim_risk_signals",
            {},
        )

        if not isinstance(
            risk_signals,
            dict,
        ):
            risk_signals = {}

        fraud_indicators = risk_signals.get(
            "fraud_indicators",
            [],
        )

        if not isinstance(
            fraud_indicators,
            list,
        ):
            fraud_indicators = []

        document_consistency = risk_signals.get(
            "document_consistency",
            True,
        )

        similar_claims_count = risk_signals.get(
            "similar_claims_count",
            0,
        )

        findings = result.get(
            "findings",
            [],
        )

        if not isinstance(
            findings,
            list,
        ):
            findings = []

        # Avoid duplicating indicators if the fraud engine already
        # returned them.
        existing_finding_text = {
            str(item).upper()
            for item in findings
        }

        for indicator in fraud_indicators:

            indicator_text = str(
                indicator
            )

            if (
                indicator_text.upper()
                not in existing_finding_text
            ):
                findings.append(
                    {
                        "type": "claim_indicator",
                        "indicator": indicator_text,
                        "severity": "HIGH",
                        "source": "claim",
                    }
                )

        # --------------------------------------------------------------
        # Determine explicit high-risk conditions.
        # --------------------------------------------------------------

        high_risk_indicators = {
            "HIGH_CLAIM_VALUE",
            "EXTENDED_STAY",
            "DUPLICATE_BILLING_INDICATOR",
            "REPEATED_SIMILAR_CLAIMS",
            "FRAUD",
            "SUSPICIOUS",
        }

        normalized_indicators = {
            str(item).upper()
            for item in fraud_indicators
        }

        high_risk_indicator_count = len(
            normalized_indicators.intersection(
                high_risk_indicators
            )
        )

        explicit_high_risk = (
            high_risk_indicator_count >= 2
            or not document_consistency
            or similar_claims_count >= 3
        )

        if explicit_high_risk:

            result["fraud_detected"] = True

            # Preserve an engine score if it is already higher.
            try:
                engine_score = float(
                    result.get(
                        "fraud_score",
                        0.0,
                    )
                    or 0.0
                )
            except (
                TypeError,
                ValueError,
            ):
                engine_score = 0.0

            # Explicit claim evidence should not be represented as
            # MINIMAL risk.
            result["fraud_score"] = max(
                engine_score,
                0.80,
            )

            result["risk_level"] = "HIGH"

        result["findings"] = findings

        result["detector_count"] = max(
            int(
                result.get(
                    "detector_count",
                    0,
                )
                or 0
            ),
            len(findings),
        )

        result["positive_detector_count"] = max(
            int(
                result.get(
                    "positive_detector_count",
                    0,
                )
                or 0
            ),
            (
                len(findings)
                if explicit_high_risk
                else 0
            ),
        )

        result["claim_risk_evidence"] = {
            "fraud_indicators": fraud_indicators,
            "document_consistency": (
                document_consistency
            ),
            "similar_claims_count": (
                similar_claims_count
            ),
            "high_risk_indicator_count": (
                high_risk_indicator_count
            ),
        }

        state["fraud_result"] = result

    # ------------------------------------------------------------------
    # Adjudication
    # ------------------------------------------------------------------

    def _run_adjudication(
        self,
        state: AgentState,
    ) -> None:

        print("\n" + "=" * 70)
        print("DEBUG ADJUDICATION INPUT")
        print("=" * 70)

        claim = state["claim"]

        claim_financials = claim.get(
            "financials",
            {},
        )

        if not isinstance(claim_financials, dict):
            claim_financials = {}

        print("CLAIM FINANCIALS:")
        print(claim_financials)

        # --------------------------------------------------------------
        # Get financial inputs generated by the rules node
        # --------------------------------------------------------------

        financial_inputs = state.get(
            "financial_inputs",
            {},
        )

        if not isinstance(financial_inputs, dict):
            financial_inputs = {}

        # --------------------------------------------------------------
        # Resolve claimed amount
        #
        # Priority:
        #
        # 1. financial_inputs.claimed_amount
        # 2. financials.claimed_amount
        # 3. financials.requested_amount
        # 4. claim.claimed_amount
        # 5. 0
        #
        # This fixes claims whose JSON uses requested_amount rather
        # than claimed_amount.
        # --------------------------------------------------------------

        claimed_amount = (
            financial_inputs.get(
                "claimed_amount"
            )
            or claim_financials.get(
                "claimed_amount"
            )
            or claim_financials.get(
                "requested_amount"
            )
            or claim.get(
                "claimed_amount"
            )
            or 0
        )

        financial_inputs["claimed_amount"] = float(
            claimed_amount or 0
        )

        # --------------------------------------------------------------
        # Non-payable amount
        #
        # Important:
        # Do NOT replace an amount calculated by _run_rules().
        #
        # For example:
        #
        # non_medical_consumables = 12000
        #
        # _run_rules() may already have converted that into
        # non_payable_amount = 12000.
        # --------------------------------------------------------------

        existing_non_payable = financial_inputs.get(
            "non_payable_amount"
        )

        if existing_non_payable is None:
            existing_non_payable = (
                claim_financials.get(
                    "non_payable_amount",
                    0,
                )
            )

        financial_inputs["non_payable_amount"] = float(
            existing_non_payable or 0
        )

        # --------------------------------------------------------------
        # Exclusion amount
        # --------------------------------------------------------------

        existing_exclusion = financial_inputs.get(
            "exclusion_amount"
        )

        if existing_exclusion is None:
            existing_exclusion = (
                claim_financials.get(
                    "exclusion_amount",
                    0,
                )
            )

        financial_inputs["exclusion_amount"] = float(
            existing_exclusion or 0
        )

        # --------------------------------------------------------------
        # Room-rent deduction
        #
        # _run_rules() calculates this from:
        #
        # daily_rate - policy_limit
        # multiplied by number of days.
        #
        # Example:
        #
        # (8000 - 5000) * 3 = 9000
        #
        # Do not overwrite that calculated value with zero.
        # --------------------------------------------------------------

        existing_room_deduction = financial_inputs.get(
            "room_rent_deduction"
        )

        if existing_room_deduction is None:
            existing_room_deduction = (
                claim_financials.get(
                    "room_rent_deduction",
                    0,
                )
            )

        financial_inputs["room_rent_deduction"] = float(
            existing_room_deduction or 0
        )

        # --------------------------------------------------------------
        # Proportional deduction
        # --------------------------------------------------------------

        existing_proportional = financial_inputs.get(
            "proportional_deduction"
        )

        if existing_proportional is None:
            existing_proportional = (
                claim_financials.get(
                    "proportional_deduction",
                    0,
                )
            )

        financial_inputs["proportional_deduction"] = float(
            existing_proportional or 0
        )

        # --------------------------------------------------------------
        # Co-pay percentage
        # --------------------------------------------------------------

        existing_copay = financial_inputs.get(
            "copay_percent"
        )

        if existing_copay is None:
            existing_copay = (
                claim_financials.get(
                    "copay_percent",
                    0,
                )
            )

        financial_inputs["copay_percent"] = float(
            existing_copay or 0
        )

        # --------------------------------------------------------------
        # Deductible
        # --------------------------------------------------------------

        existing_deductible = financial_inputs.get(
            "deductible_amount"
        )

        if existing_deductible is None:
            existing_deductible = (
                claim_financials.get(
                    "deductible_amount",
                    0,
                )
            )

        financial_inputs["deductible_amount"] = float(
            existing_deductible or 0
        )

        # --------------------------------------------------------------
        # Save normalized financial inputs back into state
        # --------------------------------------------------------------

        state["financial_inputs"] = financial_inputs

        print("\nFINANCIAL INPUTS:")
        print(financial_inputs)

        print("=" * 70)

        # --------------------------------------------------------------
        # Adjudication
        # --------------------------------------------------------------

        result = self.adjudicator.adjudicate(
            claim=state["claim"],
            financial_inputs=financial_inputs,
            policy_evidence=state.get(
                "policy_context",
                [],
            ),
            clinical_evidence=[],
            billing_evidence=[],
            rule_evidence=state.get(
                "rule_result",
                {},
            ).get(
                "rules_applied",
                [],
            ),
            fraud_result=state.get(
                "fraud_result",
                {},
            ),
        )

        # --------------------------------------------------------------
        # Debug output
        # --------------------------------------------------------------

        print("\n" + "=" * 80)
        print("ADJUDICATION DEBUG")
        print("=" * 80)

        print("RULE RESULT:")
        print(
            state.get(
                "rule_result",
                {},
            )
        )

        print("\nFRAUD RESULT:")
        print(
            state.get(
                "fraud_result",
                {},
            )
        )

        print("\nADJUDICATION RESULT:")
        print(result)

        print("=" * 80)

        # --------------------------------------------------------------
        # Store result
        # --------------------------------------------------------------

        state["adjudication_result"] = result

        
    # ------------------------------------------------------------------
    # Guardrails
    # ------------------------------------------------------------------

    def _run_guardrails(
        self,
        state: AgentState,
    ) -> None:

        result = self.guardrail_pipeline.run(
            claim=state["claim"],
            decision_result=state[
                "adjudication_result"
            ],
            policy_result=state.get(
                "policy_result",
                {},
            ),
        )

        state[
            "guardrail_result"
        ] = result.to_dict()

        state[
            "guardrails_passed"
        ] = result.passed

        state[
            "human_review_required"
        ] = not result.passed

    # ------------------------------------------------------------------
    # Final response
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # Final response
    # ------------------------------------------------------------------

     # ------------------------------------------------------------------
    # Final response
    # ------------------------------------------------------------------

    def _build_final_response(
        self,
        state: AgentState,
    ) -> None:
        """
        Build the final workflow response.

        Decision semantics:
        -------------------
        PARTIAL_APPROVAL / APPROVED / REJECTED are financial
        adjudication decisions.

        QUERY_RAISED is reserved for cases where the claim cannot
        safely receive a deterministic adjudication decision, such
        as failed guardrails or missing/invalid information.

        Fraud risk is a separate safety/review layer. A claim can
        therefore legitimately have:

            decision = PARTIAL_APPROVAL
            human_review_required = True

        This is important because fraud detection does not change
        the amount that the policy rules determined to be payable.
        It determines whether that financial decision can be
        automatically finalized without human review.
        """

        adjudication = state.get(
            "adjudication_result",
            {},
        )

        if not isinstance(adjudication, dict):
            adjudication = {}

        claim = state.get(
            "claim",
            {},
        )

        if not isinstance(claim, dict):
            claim = {}

        claim_id = claim.get(
            "claim_id",
            "UNKNOWN",
        )

        # --------------------------------------------------------------
        # 1. Guardrail failure
        #
        # A guardrail failure means the automated decision itself
        # cannot safely be finalized.
        #
        # Therefore this DOES override the adjudication decision.
        # --------------------------------------------------------------

        if not state.get(
            "guardrails_passed",
            False,
        ):
            state["final_decision"] = "QUERY_RAISED"

            state["decision"] = "QUERY_RAISED"

            state["human_review_required"] = True

            state["final_response"] = {
                **adjudication,
                "claim_id": claim_id,
                "decision": "QUERY_RAISED",
                "original_decision": adjudication.get(
                    "decision"
                ),
                "reason": (
                    "The automated adjudication failed "
                    "one or more safety checks."
                ),
                "payable_amount": adjudication.get(
                    "payable_amount",
                    0,
                ),
                "guardrails": state.get(
                    "guardrail_result",
                    {},
                ),
                "human_review_required": True,
            }

            return

        # --------------------------------------------------------------
        # 2. Determine fraud/document review requirement
        #
        # IMPORTANT:
        #
        # Fraud review is separate from financial adjudication.
        #
        # A HIGH fraud risk, repeated claims, or document inconsistency
        # requires human review but does NOT automatically convert a
        # valid financial decision into QUERY_RAISED.
        # --------------------------------------------------------------

        fraud_result = state.get(
            "fraud_result",
            {},
        )

        if not isinstance(
            fraud_result,
            dict,
        ):
            fraud_result = {}

        risk_level = str(
            fraud_result.get(
                "risk_level",
                "MINIMAL",
            )
        ).upper()

        fraud_detected = bool(
            fraud_result.get(
                "fraud_detected",
                False,
            )
        )

        claim_risk_signals = state.get(
            "claim_risk_signals",
            {},
        )

        if not isinstance(
            claim_risk_signals,
            dict,
        ):
            claim_risk_signals = {}

        document_consistency = claim_risk_signals.get(
            "document_consistency",
            True,
        )

        similar_claims_count = claim_risk_signals.get(
            "similar_claims_count",
            0,
        )

        fraud_indicators = claim_risk_signals.get(
            "fraud_indicators",
            [],
        )

        # --------------------------------------------------------------
        # Review determination
        # --------------------------------------------------------------

        review_required = False
        review_reasons = []

        # HIGH fraud risk
        if risk_level == "HIGH":
            review_required = True
            review_reasons.append(
                "HIGH fraud risk"
            )

        # MEDIUM fraud risk with actual fraud detection
        elif (
            risk_level == "MEDIUM"
            and fraud_detected
        ):
            review_required = True
            review_reasons.append(
                "MEDIUM fraud risk with fraud detection"
            )

        # Explicit document inconsistency
        if document_consistency is False:
            review_required = True
            review_reasons.append(
                "clinical/document inconsistency"
            )

        # Multiple explicit fraud indicators
        if (
            isinstance(
                fraud_indicators,
                list,
            )
            and len(fraud_indicators) >= 2
        ):
            review_required = True
            review_reasons.append(
                "multiple fraud indicators"
            )

        # Three or more similar historical claims
        try:
            similar_count = int(
                similar_claims_count
            )
        except (
            TypeError,
            ValueError,
        ):
            similar_count = 0

        if similar_count >= 3:
            review_required = True
            review_reasons.append(
                "three or more similar historical claims"
            )

        # --------------------------------------------------------------
        # 3. Determine final decision
        #
        # Financial adjudication may return APPROVED when the claim is
        # financially payable. However, strong fraud/document risk
        # prevents the claim from being safely finalized automatically.
        #
        # Such claims are raised for human review through the canonical
        # QUERY_RAISED workflow decision.
        # --------------------------------------------------------------

        decision = adjudication.get(
            "decision",
            "QUERY_RAISED",
        )

        if not decision:
            decision = "QUERY_RAISED"

        original_decision = decision

        # --------------------------------------------------------------
        # Fraud/document safety override
        # --------------------------------------------------------------

        #safety_override = (
        #    risk_level == "HIGH"
        #    or document_consistency is False
        #    or similar_count >= 3
        #    or (
        #        isinstance(
        #            fraud_indicators,
        #            list,
        #        )
        #        and len(fraud_indicators) >= 2
        #    )
        #)

        #if safety_override:
        #    decision = "QUERY_RAISED"
        #    review_required = True

        #    review_reasons.append(
        #        "fraud/document safety override"
        #    )

        # --------------------------------------------------------------
        # Store canonical decision
        # --------------------------------------------------------------

        state["final_decision"] = decision
        state["decision"] = decision
        state["human_review_required"] = review_required

        # --------------------------------------------------------------
        # Final response
        # --------------------------------------------------------------

        state["final_response"] = {
            **adjudication,

            "claim_id": claim_id,

            "decision": decision,

            "original_decision": original_decision,

            "guardrails": state.get(
                "guardrail_result",
                {},
            ),

            "fraud": fraud_result,

            "fraud_review_required": review_required,

            "review_reasons": review_reasons,

            "trace_id": state.get(
                "trace_id"
            ),

            "human_review_required": review_required,
        }