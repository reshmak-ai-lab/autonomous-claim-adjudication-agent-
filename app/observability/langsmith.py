"""
LangSmith observability integration.

LangSmith is optional. The application should continue working
when LangSmith is disabled or credentials are unavailable.
"""

import os
from typing import Any, Dict, Optional


def is_langsmith_enabled() -> bool:
    """
    Return True when LangSmith tracing is explicitly enabled.
    """

    value = os.getenv(
        "LANGCHAIN_TRACING_V2",
        os.getenv("LANGSMITH_TRACING", "false"),
    )

    return str(value).lower() in {
        "true",
        "1",
        "yes",
        "on",
    }


def get_langsmith_config() -> Dict[str, Any]:
    """
    Return the current LangSmith configuration.

    Secrets are intentionally not returned.
    """

    return {
        "enabled": is_langsmith_enabled(),
        "project": os.getenv(
            "LANGCHAIN_PROJECT",
            os.getenv(
                "LANGSMITH_PROJECT",
                "autonomous-claim-adjudication",
            ),
        ),
        "endpoint": os.getenv(
            "LANGCHAIN_ENDPOINT",
            "https://api.smith.langchain.com",
        ),
        "environment": os.getenv(
            "APP_ENV",
            "development",
        ),
    }


def configure_langsmith() -> Dict[str, Any]:
    """
    Configure environment variables used by LangChain/LangSmith.

    Returns configuration status without exposing API keys.
    """

    config = get_langsmith_config()

    if not config["enabled"]:
        return {
            "enabled": False,
            "configured": False,
            "message": "LangSmith tracing is disabled.",
        }

    api_key = os.getenv(
        "LANGCHAIN_API_KEY",
        os.getenv("LANGSMITH_API_KEY"),
    )

    if not api_key:
        return {
            "enabled": True,
            "configured": False,
            "message": (
                "LangSmith tracing is enabled but no API key "
                "was configured."
            ),
        }

    os.environ.setdefault(
        "LANGCHAIN_TRACING_V2",
        "true",
    )

    os.environ.setdefault(
        "LANGCHAIN_PROJECT",
        config["project"],
    )

    os.environ.setdefault(
        "LANGCHAIN_ENDPOINT",
        config["endpoint"],
    )

    return {
        "enabled": True,
        "configured": True,
        "project": config["project"],
        "message": "LangSmith tracing configured.",
    }


def get_langsmith_run_config(
    claim_id: Optional[str] = None,
    workflow_name: Optional[str] = None,
    tags: Optional[list[str]] = None,
) -> Dict[str, Any]:
    """
    Build metadata suitable for LangChain Runnable configuration.
    """

    metadata = {}

    if claim_id:
        metadata["claim_id"] = claim_id

    if workflow_name:
        metadata["workflow"] = workflow_name

    return {
        "tags": tags or [],
        "metadata": metadata,
    }