"""
Evidence builder.

Creates an auditable explanation for the adjudication decision.
"""

from typing import Any, Dict, List


class EvidenceBuilder:

    def build(
        self,
        claim: Dict[str, Any],
        policy_evidence: List[Dict[str, Any]] | None = None,
        clinical_evidence: List[Dict[str, Any]] | None = None,
        billing_evidence: List[Dict[str, Any]] | None = None,
        rule_evidence: List[Dict[str, Any]] | None = None,
        fraud_evidence: List[Dict[str, Any]] | None = None,
    ) -> Dict[str, Any]:

        policy_evidence = policy_evidence or []
        clinical_evidence = clinical_evidence or []
        billing_evidence = billing_evidence or []
        rule_evidence = rule_evidence or []
        fraud_evidence = fraud_evidence or []

        all_evidence = []

        all_evidence.extend(policy_evidence)
        all_evidence.extend(clinical_evidence)
        all_evidence.extend(billing_evidence)
        all_evidence.extend(rule_evidence)
        all_evidence.extend(fraud_evidence)

        return {
            "claim_id": claim.get("claim_id"),
            "evidence_count": len(all_evidence),
            "policy_evidence": policy_evidence,
            "clinical_evidence": clinical_evidence,
            "billing_evidence": billing_evidence,
            "rule_evidence": rule_evidence,
            "fraud_evidence": fraud_evidence,
            "all_evidence": all_evidence,
        }