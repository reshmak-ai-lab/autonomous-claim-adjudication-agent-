"""
State definition for the claim adjudication agent.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, TypedDict


class AgentState(TypedDict, total=False):

    # ------------------------------------------------------------------
    # Claim context
    # ------------------------------------------------------------------

    claim_id: str
    claim: Dict[str, Any]

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

    documents: List[Dict[str, Any]]
    document_metadata: List[Dict[str, Any]]

    # ------------------------------------------------------------------
    # Extraction
    # ------------------------------------------------------------------

    clinical_data: Dict[str, Any]
    billing_data: Dict[str, Any]
    diagnosis_data: Dict[str, Any]
    procedure_data: Dict[str, Any]
    timeline_data: Dict[str, Any]

    # ------------------------------------------------------------------
    # Policy / RAG
    # ------------------------------------------------------------------

    policy_context: List[Dict[str, Any]]
    policy_result: Dict[str, Any]

    # ------------------------------------------------------------------
    # Rules
    # ------------------------------------------------------------------

    rule_result: Dict[str, Any]
    financial_inputs: Dict[str, Any]

    # ------------------------------------------------------------------
    # Fraud
    # ------------------------------------------------------------------

    fraud_result: Dict[str, Any]

    # ------------------------------------------------------------------
    # Adjudication
    # ------------------------------------------------------------------

    adjudication_result: Dict[str, Any]

    # ------------------------------------------------------------------
    # Guardrails
    # ------------------------------------------------------------------

    guardrail_result: Dict[str, Any]
    guardrails_passed: bool
    human_review_required: bool

    # ------------------------------------------------------------------
    # Final response
    # ------------------------------------------------------------------

    final_decision: str
    final_response: Dict[str, Any]

    # ------------------------------------------------------------------
    # Observability
    # ------------------------------------------------------------------

    trace_id: str
    execution_trace: List[Dict[str, Any]]
    errors: List[str]
    warnings: List[str]