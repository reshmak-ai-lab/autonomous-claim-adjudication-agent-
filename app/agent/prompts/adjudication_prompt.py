"""
Prompt for generating an adjudication explanation.
"""

ADJUDICATION_PROMPT = """
Review the claim adjudication information below.

Claim:
{claim}

Policy evidence:
{policy_context}

Clinical evidence:
{clinical_data}

Billing information:
{billing_data}

Rule evaluation:
{rule_result}

Fraud assessment:
{fraud_result}

Financial calculation:
{financial_inputs}

Determine the appropriate adjudication recommendation.

Rules:

- Do not invent missing information.
- Do not override deterministic rules.
- Do not approve excluded claims.
- Do not approve claims with invalid financial calculations.
- If required information is missing, recommend QUERY_RAISED.
- If fraud risk requires investigation, recommend human review.
- Clearly explain the evidence supporting the recommendation.

Return:

Decision:
Reason:
Key evidence:
Financial impact:
Fraud considerations:
Human review required:
"""