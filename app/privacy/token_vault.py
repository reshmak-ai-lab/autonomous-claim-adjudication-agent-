import secrets
from typing import Optional


class TokenVault:
    """
    In-memory reversible token vault.

    Production implementation should use encrypted persistent
    storage or a dedicated secrets-management system.
    """

    def __init__(self):
        self._tokens: dict[str, str] = {}

    def create_token(
        self,
        sensitive_value: str,
        entity_type: str,
    ) -> str:

        token = (
            f"<{entity_type}_"
            f"{secrets.token_hex(8)}>"
        )

        self._tokens[token] = sensitive_value

        return token

    def resolve(
        self,
        token: str,
    ) -> Optional[str]:

        return self._tokens.get(token)

    def delete(
        self,
        token: str,
    ) -> bool:

        if token in self._tokens:
            del self._tokens[token]
            return True

        return False

    def clear(self) -> None:
        self._tokens.clear()

    def size(self) -> int:
        return len(self._tokens)