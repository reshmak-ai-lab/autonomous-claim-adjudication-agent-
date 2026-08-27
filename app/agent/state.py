"""
State definition for the claim adjudication agent.
"""

from __future__ import annotations

from typing import Any, dict, List, Optional, Typeddict


class AgentState(Typeddict, total=False):

    # ------------------------------------------------------------------
    # Claim context
    # ------------------------------------------------------------------

    claim_id: str
    claim: dict[str, Any]

    patient_id: Optional[str]
    policy_id: Optional[str]

    # ------------------------------------------------------------------
    # Input / privacy
    # ------------------------------------------------------------------

    raw_input: str
    sanitized_input: str
    pii_detected: bool

    # ------------------------------------------------------------------
    # Documents
    # ------------------------------------------------------------------

    documents: List[dict[str, Any]]
    document_metadata: List[dict[str, Any]]

    # ------------------------------------------------------------------
    # Extraction
    # ------------------------------------------------------------------

    clinical_data: dict[str, Any]
    billing_data: dict[str, Any]
    diagnosis_data: dict[str, Any]
    procedure_data: dict[str, Any]
    timeline_data: dict[str, Any]

    # ------------------------------------------------------------------
    # Policy / RAG
    # ------------------------------------------------------------------

    policy_context: List[dict[str, Any]]
    policy_result: dict[str, Any]

    # ------------------------------------------------------------------
    # Rules
    # ------------------------------------------------------------------

    rule_result: dict[str, Any]
    financial_inputs: dict[str, Any]

    # ------------------------------------------------------------------
    # Fraud
    # ------------------------------------------------------------------

    fraud_result: dict[str, Any]

    # ------------------------------------------------------------------
    # Adjudication
    # ------------------------------------------------------------------

    adjudication_result: dict[str, Any]

    # ------------------------------------------------------------------
    # Guardrails
    # ------------------------------------------------------------------

    guardrail_result: dict[str, Any]
    guardrails_passed: bool
    human_review_required: bool

    # ------------------------------------------------------------------
    # Final response
    # ------------------------------------------------------------------

    final_decision: str
    final_response: dict[str, Any]

    # ------------------------------------------------------------------
    # Observability
    # ------------------------------------------------------------------

    trace_id: str
    execution_trace: List[dict[str, Any]]
    errors: List[str]
    warnings: List[str]