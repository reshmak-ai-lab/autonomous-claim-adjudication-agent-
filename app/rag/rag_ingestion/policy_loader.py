from pathlib import Path
from typing import Any


class PolicyLoader:
    """Loads policy documents from the policy directory."""

    def __init__(
        self,
        policy_dir: str = "data/policies",
    ):
        self.policy_dir = Path(policy_dir)

    def load(self) -> list[dict[str, Any]]:
        """Load all TXT policy documents."""

        if not self.policy_dir.exists():
            raise FileNotFoundError(
                f"Policy directory not found: {self.policy_dir}"
            )

        files = sorted(
            self.policy_dir.glob("*.txt")
        )

        if not files:
            raise FileNotFoundError(
                f"No policy files found in {self.policy_dir}"
            )

        documents = []

        for file_path in files:
            text = file_path.read_text(
                encoding="utf-8"
            ).strip()

            if not text:
                continue

            documents.append(
                {
                    "source": file_path.name,
                    "path": str(file_path),
                    "text": text,
                }
            )

        return documents