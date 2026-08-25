import os

import pytest
import requests


POLICY_MCP_URL = os.getenv(
    "POLICY_MCP_URL",
    "http://localhost:8004",
)

ICD10_MCP_URL = os.getenv(
    "ICD10_MCP_URL",
    "http://localhost:8005",
)

TARIFF_MCP_URL = os.getenv(
    "TARIFF_MCP_URL",
    "http://localhost:8006",
)

CALCULATION_MCP_URL = os.getenv(
    "CALCULATION_MCP_URL",
    "http://localhost:8007",
)

FRAUD_MCP_URL = os.getenv(
    "FRAUD_MCP_URL",
    "http://localhost:8001",
)

LEDGER_MCP_URL = os.getenv(
    "LEDGER_MCP_URL",
    "http://localhost:8002",
)

COMPLIANCE_MCP_URL = os.getenv(
    "COMPLIANCE_MCP_URL",
    "http://localhost:8003",
)


def service_available(url: str) -> bool:
    try:
        response = requests.get(
            f"{url}/health",
            timeout=2,
        )
        return response.status_code == 200
    except requests.RequestException:
        return False


# ============================================================
# POLICY MCP
# ============================================================


def test_policy_mcp_health():

    if not service_available(POLICY_MCP_URL):
        pytest.skip("Policy MCP service is not running.")

    response = requests.get(
        f"{POLICY_MCP_URL}/health",
        timeout=5,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"


def test_policy_mcp_search_policy():

    if not service_available(POLICY_MCP_URL):
        pytest.skip("Policy MCP service is not running.")

    response = requests.post(
        f"{POLICY_MCP_URL}/tools/search-policy",
        json={
            "query": "room rent",
        },
        timeout=5,
    )

    assert response.status_code == 200

    data = response.json()

    assert data is not None


def test_policy_mcp_get_policy():

    if not service_available(POLICY_MCP_URL):
        pytest.skip("Policy MCP service is not running.")

    response = requests.get(
        f"{POLICY_MCP_URL}/tools/get-policy/POL-001",
        timeout=5,
    )

    assert response.status_code == 200

    data = response.json()

    assert data is not None


# ============================================================
# ICD10 MCP
# ============================================================


def test_icd10_mcp_health():

    if not service_available(ICD10_MCP_URL):
        pytest.skip("ICD10 MCP service is not running.")

    response = requests.get(
        f"{ICD10_MCP_URL}/health",
        timeout=5,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"


def test_icd10_mcp_lookup():

    if not service_available(ICD10_MCP_URL):
        pytest.skip("ICD10 MCP service is not running.")

    response = requests.post(
        f"{ICD10_MCP_URL}/tools/lookup-icd10",
        json={
            "code": "K35.80",
        },
        timeout=5,
    )

    assert response.status_code == 200

    data = response.json()

    assert data is not None


def test_icd10_mcp_search_diagnosis():

    if not service_available(ICD10_MCP_URL):
        pytest.skip("ICD10 MCP service is not running.")

    response = requests.post(
        f"{ICD10_MCP_URL}/tools/search-diagnosis",
        json={
            "query": "appendicitis",
        },
        timeout=5,
    )

    assert response.status_code == 200

    data = response.json()

    assert data is not None


# ============================================================
# TARIFF MCP
# ============================================================


def test_tariff_mcp_health():

    if not service_available(TARIFF_MCP_URL):
        pytest.skip("Tariff MCP service is not running.")

    response = requests.get(
        f"{TARIFF_MCP_URL}/health",
        timeout=5,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"


def test_tariff_mcp_get_tariff():

    if not service_available(TARIFF_MCP_URL):
        pytest.skip("Tariff MCP service is not running.")

    response = requests.get(
        f"{TARIFF_MCP_URL}/tools/get-tariff/APPENDECTOMY",
        timeout=5,
    )

    assert response.status_code == 200

    data = response.json()

    assert data is not None


def test_tariff_mcp_search_procedure():

    if not service_available(TARIFF_MCP_URL):
        pytest.skip("Tariff MCP service is not running.")

    response = requests.post(
        f"{TARIFF_MCP_URL}/tools/search-procedure",
        json={
            "query": "appendectomy",
        },
        timeout=5,
    )

    assert response.status_code == 200

    data = response.json()

    assert data is not None


# ============================================================
# CALCULATION MCP
# ============================================================


def test_calculation_mcp_health():

    if not service_available(CALCULATION_MCP_URL):
        pytest.skip(
            "Calculation MCP service is not running."
        )

    response = requests.get(
        f"{CALCULATION_MCP_URL}/health",
        timeout=5,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"


def test_calculation_mcp_copay():

    if not service_available(CALCULATION_MCP_URL):
        pytest.skip(
            "Calculation MCP service is not running."
        )

    response = requests.post(
        f"{CALCULATION_MCP_URL}/tools/calculate-copay",
        json={
            "eligible_amount": 10000,
            "copay_percentage": 20,
        },
        timeout=5,
    )

    assert response.status_code == 200

    data = response.json()

    assert data is not None


def test_calculation_mcp_deductible():

    if not service_available(CALCULATION_MCP_URL):
        pytest.skip(
            "Calculation MCP service is not running."
        )

    response = requests.post(
        f"{CALCULATION_MCP_URL}/tools/calculate-deductible",
        json={
            "eligible_amount": 10000,
            "deductible": 2000,
        },
        timeout=5,
    )

    assert response.status_code == 200

    data = response.json()

    assert data is not None


def test_calculation_mcp_proportional_deduction():

    if not service_available(CALCULATION_MCP_URL):
        pytest.skip(
            "Calculation MCP service is not running."
        )

    response = requests.post(
        f"{CALCULATION_MCP_URL}/tools/calculate-proportional-deduction",
        json={
            "actual_room_rent": 6000,
            "eligible_room_rent": 4000,
            "bill_amount": 20000,
        },
        timeout=5,
    )

    assert response.status_code == 200

    data = response.json()

    assert data is not None


def test_calculation_mcp_final_payable():

    if not service_available(CALCULATION_MCP_URL):
        pytest.skip(
            "Calculation MCP service is not running."
        )

    response = requests.post(
        f"{CALCULATION_MCP_URL}/tools/calculate-final-payable",
        json={
            "eligible_amount": 50000,
            "deductible": 5000,
            "copay_percentage": 10,
        },
        timeout=5,
    )

    assert response.status_code == 200

    data = response.json()

    assert data is not None


# ============================================================
# FRAUD MCP
# ============================================================


def test_fraud_mcp_health():

    if not service_available(FRAUD_MCP_URL):
        pytest.skip("Fraud MCP service is not running.")

    response = requests.get(
        f"{FRAUD_MCP_URL}/health",
        timeout=5,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"


def test_fraud_mcp_analyze_fraud():

    if not service_available(FRAUD_MCP_URL):
        pytest.skip("Fraud MCP service is not running.")

    response = requests.post(
        f"{FRAUD_MCP_URL}/tools/analyze-fraud",
        json={
            "transaction_id": "TXN-10025",
            "amount": 7500,
            "merchant_id": "merchant_001",
            "country": "india",
        },
        timeout=5,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["source"] == "fraud_mcp"

    fraud_data = data["data"]

    assert "risk_score" in fraud_data
    assert "risk_level" in fraud_data
    assert "fraud_detected" in fraud_data


# ============================================================
# LEDGER MCP
# ============================================================


def test_ledger_mcp_health():

    if not service_available(LEDGER_MCP_URL):
        pytest.skip("Ledger MCP service is not running.")

    response = requests.get(
        f"{LEDGER_MCP_URL}/health",
        timeout=5,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"


def test_ledger_mcp_get_transaction():

    if not service_available(LEDGER_MCP_URL):
        pytest.skip("Ledger MCP service is not running.")

    response = requests.get(
        f"{LEDGER_MCP_URL}/tools/get-transaction/TXN-10025",
        timeout=5,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["found"] is True


def test_ledger_mcp_get_balance():

    if not service_available(LEDGER_MCP_URL):
        pytest.skip("Ledger MCP service is not running.")

    response = requests.get(
        f"{LEDGER_MCP_URL}/tools/get-balance/merchant_001",
        timeout=5,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["balance"] >= 0


# ============================================================
# COMPLIANCE MCP
# ============================================================


def test_compliance_mcp_health():

    if not service_available(COMPLIANCE_MCP_URL):
        pytest.skip(
            "Compliance MCP service is not running."
        )

    response = requests.get(
        f"{COMPLIANCE_MCP_URL}/health",
        timeout=5,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"


def test_compliance_mcp_check():

    if not service_available(COMPLIANCE_MCP_URL):
        pytest.skip(
            "Compliance MCP service is not running."
        )

    response = requests.post(
        f"{COMPLIANCE_MCP_URL}/tools/check-compliance",
        json={
            "merchant_id": "merchant_001",
            "transaction_id": "TXN-10025",
            "country": "india",
            "amount": 7500,
        },
        timeout=5,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["source"] == "compliance_mcp"

    compliance = data["data"]

    assert "compliant" in compliance
    assert "violations" in compliance
    assert "review_required" in compliance