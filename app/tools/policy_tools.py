from pathlib import Path
from typing import Any


class PolicyTools:
    """Tools for searching and validating insurance policy rules."""

    def __init__(self, policy_dir: str = "data/policies"):
        self.policy_dir = Path(policy_dir)

    def search_policy(
        self,
        query: str,
        max_results: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Search policy documents using simple keyword matching.

        Returns matching text snippets with source information.
        """

        if not query or not query.strip():
            return []

        if not self.policy_dir.exists():
            return []

        query_terms = {
            word.lower()
            for word in query.split()
            if len(word) > 2
        }

        results = []

        for policy_file in self.policy_dir.glob("*.txt"):
            try:
                text = policy_file.read_text(
                    encoding="utf-8"
                )
            except OSError:
                continue

            lines = text.splitlines()

            for line_number, line in enumerate(lines, start=1):
                line_lower = line.lower()

                matched_terms = [
                    term
                    for term in query_terms
                    if term in line_lower
                ]

                if matched_terms:
                    results.append(
                        {
                            "source": policy_file.name,
                            "line": line_number,
                            "text": line.strip(),
                            "matched_terms": matched_terms,
                        }
                    )

                if len(results) >= max_results:
                    return results

        return results

    def get_policy_document(
        self,
        filename: str,
    ) -> dict[str, Any]:
        """Return the complete contents of a policy document."""

        file_path = self.policy_dir / filename

        if not file_path.exists():
            return {
                "success": False,
                "error": f"Policy not found: {filename}",
            }

        try:
            text = file_path.read_text(
                encoding="utf-8"
            )
        except OSError as exc:
            return {
                "success": False,
                "error": str(exc),
            }

        return {
            "success": True,
            "source": filename,
            "content": text,
        }