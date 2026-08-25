from __future__ import annotations

from typing import Any

import requests


class MCPClient:

    def __init__(
        self,
        base_url: str,
        timeout: float = 10.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def call_tool(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        url = f"{self.base_url}/{path.lstrip('/')}"

        if method.upper() == "GET":
            response = requests.get(
                url,
                timeout=self.timeout,
            )
        else:
            response = requests.post(
                url,
                json=payload or {},
                timeout=self.timeout,
            )

        response.raise_for_status()

        return response.json()

    def health_check(self) -> dict[str, Any]:

        response = requests.get(
            f"{self.base_url}/health",
            timeout=self.timeout,
        )

        response.raise_for_status()

        return response.json()