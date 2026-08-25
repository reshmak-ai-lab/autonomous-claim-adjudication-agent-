"""
Prompt for fraud-risk reasoning.
"""

FRAUD_PROMPT = """
Analyze the following claim for potential fraud indicators.

Claim:
{claim}

Clinical information:
{clinical_data}

Billing information:
{billing_data}

Timeline:
{timeline_data}

Detected fraud signals:
{fraud_result}

You must:

1. Distinguish fraud signals from confirmed fraud.
2. Never state that fraud is confirmed solely because an anomaly exists.
3. Identify duplicate charges.
4. Identify possible unbundling.
5. Identify timeline inconsistencies.
6. Identify clinical-billing mismatches.
7. Consider unusual billing amounts.
8. Recommend human investigation when appropriate.

Return:

Risk level:
Fraud score:
Detected signals:
Explanation:
Human review required:
"""