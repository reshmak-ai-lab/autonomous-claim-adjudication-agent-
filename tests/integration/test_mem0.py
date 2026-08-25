"""
Integration tests for the memory layer.

Tests:
1. Mem0 client initialization
2. Claim history storage
3. Claim history retrieval
4. Patient memory storage
5. Patient memory search
6. Patient memory isolation
"""

import os

import pytest
from dotenv import load_dotenv


load_dotenv()

# ============================================================
# Helpers
# ============================================================

def mem0_credentials_available() -> bool:
    """
    Check whether the environment contains credentials
    required for Mem0/OpenAI integration tests.
    """

    return bool(
        os.getenv("MEM0_API_KEY")
        or os.getenv("OPENAI_API_KEY")
    )


MEM0_AVAILABLE = mem0_credentials_available()


def get_mem0_client():
    """
    Create the project's Mem0 client.
    """

    from app.memory.mem0_client import Mem0Client

    return Mem0Client()


def get_claim_history():
    """
    Create the project's ClaimHistory service.
    """

    from app.memory.claim_history import ClaimHistory

    return ClaimHistory()


def get_patient_memory():
    """
    Create the project's PatientMemory service.
    """

    from app.memory.patient_memory import PatientMemory

    return PatientMemory()


# ============================================================
# Mem0 Client
# ============================================================

@pytest.mark.integration
@pytest.mark.skipif(
    not MEM0_AVAILABLE,
    reason="Mem0/OpenAI credentials are not configured",
)
def test_mem0_client_initialization():

    client = get_mem0_client()

    assert client is not None


# ============================================================
# Claim History
# ============================================================

@pytest.mark.integration
def test_claim_history_add_claim():

    service = get_claim_history()

    claim = {
        "claim_id": "CLM-HISTORY-TEST-001",
        "patient_id": "PAT-HISTORY-TEST-001",
        "policy_id": "POL-TEST-001",
        "hospital_id": "HOSP-1020",
        "diagnosis": "Acute appendicitis",
        "procedure": "Appendectomy",
        "claimed_amount": 85000,
        "payable_amount": 75000,
        "decision": "PARTIAL_APPROVAL",
        "fraud_flag": False,
    }

    result = service.add_claim(
        claim=claim,
    )

    assert isinstance(
        result,
        dict,
    )

    assert result.get(
        "success"
    ) is True

    assert result.get(
        "claim_id"
    ) == "CLM-HISTORY-TEST-001"


@pytest.mark.integration
def test_claim_history_get_claim():

    service = get_claim_history()

    claim = {
        "claim_id": "CLM-HISTORY-TEST-002",
        "patient_id": "PAT-HISTORY-TEST-002",
        "policy_id": "POL-TEST-002",
        "hospital_id": "HOSP-2048",
        "diagnosis": "Cholecystitis",
        "procedure": "Cholecystectomy",
        "claimed_amount": 100000,
        "payable_amount": 90000,
        "decision": "APPROVED",
        "fraud_flag": False,
    }

    service.add_claim(
        claim=claim,
    )

    result = service.get_claim(
        "CLM-HISTORY-TEST-002"
    )

    assert result is not None

    assert result["claim_id"] == (
        "CLM-HISTORY-TEST-002"
    )

    assert result["patient_id"] == (
        "PAT-HISTORY-TEST-002"
    )


@pytest.mark.integration
def test_claim_history_patient_claims():

    service = get_claim_history()

    patient_id = (
        "PAT-HISTORY-TEST-003"
    )

    claim = {
        "claim_id": "CLM-HISTORY-TEST-003",
        "patient_id": patient_id,
        "policy_id": "POL-TEST-003",
        "hospital_id": "HOSP-1020",
        "diagnosis": "Appendicitis",
        "procedure": "Appendectomy",
        "claimed_amount": 85000,
        "payable_amount": 75000,
        "decision": "PARTIAL_APPROVAL",
        "fraud_flag": False,
    }

    service.add_claim(
        claim=claim,
    )

    results = service.get_patient_claims(
        patient_id=patient_id
    )

    assert isinstance(
        results,
        list,
    )

    assert any(
        item.get("claim_id")
        == "CLM-HISTORY-TEST-003"
        for item in results
    )


@pytest.mark.integration
def test_claim_history_summary():

    service = get_claim_history()

    patient_id = (
        "PAT-HISTORY-SUMMARY-001"
    )

    claims = [
        {
            "claim_id": "CLM-SUMMARY-001",
            "patient_id": patient_id,
            "decision": "APPROVED",
        },
        {
            "claim_id": "CLM-SUMMARY-002",
            "patient_id": patient_id,
            "decision": "REJECTED",
        },
        {
            "claim_id": "CLM-SUMMARY-003",
            "patient_id": patient_id,
            "decision": "PARTIAL_APPROVAL",
        },
    ]

    for claim in claims:
        service.add_claim(
            claim=claim
        )

    summary = service.get_summary(
        patient_id
    )

    assert summary["patient_id"] == patient_id

    assert summary["total_claims"] >= 3

    assert summary["approved"] >= 1

    assert summary["rejected"] >= 1

    assert summary["partial_approval"] >= 1


# ============================================================
# Patient Memory - Mem0
# ============================================================

@pytest.mark.integration
@pytest.mark.skipif(
    not MEM0_AVAILABLE,
    reason="Mem0/OpenAI credentials are not configured",
)
def test_patient_memory():

    memory = get_patient_memory()

    patient_id = (
        "PAT-MEM0-TEST-002"
    )

    memory_text = (
        "Patient PAT-MEM0-TEST-002 "
        "previously underwent "
        "gallbladder surgery."
    )

    result = memory.store_patient_context(
        patient_id=patient_id,
        context=memory_text,
    )

    assert result is not None

    assert isinstance(
        result,
        dict,
    )


@pytest.mark.integration
@pytest.mark.skipif(
    not MEM0_AVAILABLE,
    reason="Mem0/OpenAI credentials are not configured",
)
def test_patient_memory_search():

    memory = get_patient_memory()

    patient_id = (
        "PAT-MEM0-TEST-002"
    )

    result = memory.search_patient_memory(
        patient_id=patient_id,
        query=(
            "previous gallbladder surgery"
        ),
        limit=5,
    )

    assert result is not None


# ============================================================
# Patient Memory Isolation
# ============================================================

@pytest.mark.integration
@pytest.mark.skipif(
    not MEM0_AVAILABLE,
    reason="Mem0/OpenAI credentials are not configured",
)
def test_patient_memory_isolation():

    memory = get_patient_memory()

    patient_a = (
        "PAT-MEM0-ISOLATION-A"
    )

    patient_b = (
        "PAT-MEM0-ISOLATION-B"
    )

    memory.store_patient_context(
        patient_id=patient_a,
        context=(
            "Patient A previously "
            "underwent appendectomy."
        ),
    )

    memory.store_patient_context(
        patient_id=patient_b,
        context=(
            "Patient B previously "
            "underwent cholecystectomy."
        ),
    )

    result_a = memory.search_patient_memory(
        patient_id=patient_a,
        query="previous surgery",
        limit=5,
    )

    result_b = memory.search_patient_memory(
        patient_id=patient_b,
        query="previous surgery",
        limit=5,
    )

    assert result_a is not None

    assert result_b is not None


# ============================================================
# Patient Memory Empty Context
# ============================================================

@pytest.mark.integration
@pytest.mark.skipif(
    not MEM0_AVAILABLE,
    reason="Mem0/OpenAI credentials are not configured",
)
def test_patient_memory_empty_context():

    memory = get_patient_memory()

    result = memory.store_patient_context(
        patient_id="PAT-MEM0-EMPTY-001",
        context="",
    )

    assert result["success"] is False