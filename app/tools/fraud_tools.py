from typing import Any

from app.tools.mcp_services.client import MCPClient


def analyze_fraud(
    transaction_id: str,
    amount: float,
    merchant_id: str,
    country: str,
) -> dict[str, Any]:

    client = MCPClient(
        base_url="http://localhost:8001"
    )

    return client.call_tool(
        "/tools/analyze-fraud",
        {
            "transaction_id": transaction_id,
            "amount": amount,
            "merchant_id": merchant_id,
            "country": country,
        },
    )