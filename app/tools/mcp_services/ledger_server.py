from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI(
    title="Banking Ledger MCP Service",
    version="1.0.0",
)


TRANSACTIONS: dict[str, dict[str, Any]] = {
    "TXN-10025": {
        "transaction_id": "TXN-10025",
        "amount": 1000.0,
        "status": "completed",
        "merchant_id": "merchant_001",
    },
    "TXN-10026": {
        "transaction_id": "TXN-10026",
        "amount": 2500.0,
        "status": "completed",
        "merchant_id": "merchant_001",
    },
}


MERCHANT_BALANCES: dict[str, float] = {
    "merchant_001": 10000.0,
    "merchant_002": 25000.0,
}


class TransactionResponse(BaseModel):
    source: str
    transaction_id: str
    amount: float
    status: str
    merchant_id: str


class BalanceResponse(BaseModel):
    source: str
    merchant_id: str
    balance: float
    currency: str


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "banking_ledger_mcp",
    }


@app.get(
    "/tools/get-transaction/{transaction_id}",
    response_model=TransactionResponse,
)
def get_transaction(
    transaction_id: str,
) -> TransactionResponse:

    transaction = TRANSACTIONS.get(transaction_id)

    if transaction is None:
        transaction = {
            "transaction_id": transaction_id,
            "amount": 0.0,
            "status": "not_found",
            "merchant_id": "",
        }

    return TransactionResponse(
        source="banking_ledger_mcp",
        transaction_id=transaction["transaction_id"],
        amount=float(transaction["amount"]),
        status=transaction["status"],
        merchant_id=transaction["merchant_id"],
    )


@app.get(
    "/tools/get-balance/{merchant_id}",
    response_model=BalanceResponse,
)
def get_balance(
    merchant_id: str,
) -> BalanceResponse:

    balance = MERCHANT_BALANCES.get(
        merchant_id,
        0.0,
    )

    return BalanceResponse(
        source="banking_ledger_mcp",
        merchant_id=merchant_id,
        balance=balance,
        currency="USD",
    )