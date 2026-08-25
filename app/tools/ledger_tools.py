from typing import Any

from app.tools.mcp_services.client import MCPClient


def get_transaction(
    transaction_id: str,
) -> dict[str, Any]:

    client = MCPClient(
        base_url="http://localhost:8002"
    )

    return client.call_tool(
        f"/tools/get-transaction/{transaction_id}",
        method="GET",
    )


def get_balance(
    merchant_id: str,
) -> dict[str, Any]:

    client = MCPClient(
        base_url="http://localhost:8002"
    )

    return client.call_tool(
        f"/tools/get-balance/{merchant_id}",
        method="GET",
    )