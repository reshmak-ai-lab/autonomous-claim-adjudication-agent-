from __future__ import annotations

import os
import tempfile
import uuid
from pathlib import Path
from typing import Any



from dotenv import load_dotenv

load_dotenv(".env")

def _initialize(self) -> None:
    """
    Initialize the Mem0 client using the project's OpenAI model.
    """

    try:
        from mem0 import Memory
    except ImportError as exc:
        raise RuntimeError(
            "mem0ai is not installed. "
            "Install it with: pip install mem0ai"
        ) from exc

    model = (
        os.getenv("MEM0_LLM_MODEL")
        or os.getenv("OPENAI_MODEL")
        or os.getenv("OPENAI_MODEL_NAME")
        or "gpt-4o-mini"
    )

    print(f"Initializing Mem0 with model: {model}")

    # Temporary/default initialization.
    # The exact Memory configuration depends on your installed mem0ai version.
    self.memory = Memory()


class Mem0Client:
    """
    Application wrapper around Mem0.

    PatientMemory and other application services should use this
    class instead of importing Mem0 directly.

    The client:
    - uses an explicitly configured LLM model
    - avoids Mem0's default model selection
    - creates an isolated local Qdrant directory per client
    """

    def __init__(
        self,
        qdrant_path: str | None = None,
    ):
        self.enabled = self._is_enabled()
        self.memory = None
        #self.memory = Memory.from_config(...)

        # Give every Mem0 client its own local Qdrant directory.
        #
        # This prevents:
        #
        # RuntimeError:
        # Storage folder /tmp/qdrant is already accessed
        # by another instance of Qdrant client.
        #
        self.qdrant_path = self._get_qdrant_path(
            qdrant_path
        )

        if self.enabled:
            self._initialize()

    # ============================================================
    # Configuration
    # ============================================================

    def _is_enabled(self) -> bool:
        """
        Determine whether Mem0 should be enabled.
        """

        enabled = os.getenv(
            "MEM0_ENABLED",
            "true",
        ).strip().lower() == "true"

        if not enabled:
            return False

        return bool(
            os.getenv("MEM0_API_KEY")
            or os.getenv("OPENAI_API_KEY")
        )

    def _get_qdrant_path(
        self,
        qdrant_path: str | None = None,
    ) -> str:
        """
        Return an isolated Qdrant storage path.

        Priority:

        1. Explicit qdrant_path
        2. MEM0_QDRANT_PATH environment variable
        3. Unique temporary directory
        """

        if qdrant_path:
            path = Path(qdrant_path)
            path.mkdir(
                parents=True,
                exist_ok=True,
            )
            return str(path)

        configured_path = os.getenv(
            "MEM0_QDRANT_PATH"
        )

        if configured_path:
            path = Path(configured_path)
            path.mkdir(
                parents=True,
                exist_ok=True,
            )
            return str(path)

        # IMPORTANT:
        # Do not use /tmp/qdrant directly.
        #
        # Each Mem0Client receives its own directory.
        #
        unique_path = Path(
            tempfile.mkdtemp(
                prefix="mem0-qdrant-"
            )
        )

        return str(unique_path)

    # ============================================================
    # Initialization
    # ============================================================

    def _initialize(self) -> None:
        """
        Initialize Mem0 using explicit configuration.
        """

        try:
            from mem0 import Memory
        except ImportError as exc:
            raise RuntimeError(
                "mem0ai is not installed. "
                "Install it with: pip install mem0ai"
            ) from exc

        openai_api_key = os.getenv(
            "OPENAI_API_KEY"
        )

        mem0_api_key = os.getenv(
            "MEM0_API_KEY"
        )

        # --------------------------------------------------------
        # Explicit model configuration
        # --------------------------------------------------------
        #
        # Your current error says gpt-5-mini is being selected
        # by the default Mem0 configuration.
        #
        # We therefore explicitly configure the model.
        #
        model = os.getenv(
            "MEM0_LLM_MODEL",
               "gpt-4o-mini",
        )

        # --------------------------------------------------------
        # Build Mem0 configuration
        # --------------------------------------------------------

        config: dict[str, Any] = {
            "llm": {
                "provider": "openai",
                "config": {
                    "model": model,
                    "temperature": 0,
                },
            },

            "vector_store": {
                "provider": "qdrant",
                "config": {
                    "path": self.qdrant_path,
                    "embedding_model_dims": 1536,
                },
            },
        }

        # Add OpenAI API key when available.
        if openai_api_key:
            config["llm"]["config"]["api_key"] = (
                openai_api_key
            )

        # Some Mem0 configurations use MEM0_API_KEY for
        # hosted Mem0 functionality. Keep it available through
        # the environment rather than hard-coding it.
        if mem0_api_key:
            os.environ.setdefault(
                "MEM0_API_KEY",
                mem0_api_key,
            )

        try:
            self.memory = Memory.from_config(
                config
            )
        except AttributeError as exc:
            raise RuntimeError(
                "Installed mem0ai version does not support "
                "Memory.from_config(). "
                "Check the installed mem0ai version."
            ) from exc

    # ============================================================
    # Add memory
    # ============================================================

    def add_memory(
        self,
        messages: list[dict[str, Any]] | str,
        user_id: str,
        metadata: dict[str, Any] | None = None,
    ) -> Any:
        """
        Store a memory in Mem0.
        """

        if not self.enabled:
            return {
                "success": False,
                "reason": "Mem0 is disabled",
            }

        if self.memory is None:
            raise RuntimeError(
                "Mem0 client is not initialized."
            )

        if not user_id:
            raise ValueError(
                "user_id is required"
            )

        if isinstance(messages, str):
            messages = [
                {
                    "role": "user",
                    "content": messages,
                }
            ]

        return self.memory.add(
            messages,
            user_id=user_id,
            metadata=metadata or {},
        )

    # ============================================================
    # Search memory
    # ============================================================

    def search_memory(
        self,
        query: str,
        user_id: str,
        limit: int = 5,
    ) -> Any:
        """
        Search semantic memories for a specific user.
        """

        if not self.enabled:
            return []

        if self.memory is None:
            raise RuntimeError(
                "Mem0 client is not initialized."
            )

        if not query:
            return []

        if not user_id:
            raise ValueError(
                "user_id is required"
            )

        return self.memory.search(
            query,
            filters={"user_id": user_id},
            limit=limit,
        )

    # ============================================================
    # Get all memories
    # ============================================================

    def get_all_memory(
        self,
        user_id: str,
    ) -> Any:
        """
        Retrieve all memories for a user.
        """

        if not self.enabled:
            return []

        if self.memory is None:
            raise RuntimeError(
                "Mem0 client is not initialized."
            )

        if not user_id:
            raise ValueError(
                "user_id is required"
            )

        return self.memory.get_all(
            filters={"user_id": user_id},
        )

    # ============================================================
    # Backward-compatible aliases
    # ============================================================

    def add(
        self,
        text: str,
        user_id: str,
        metadata: dict[str, Any] | None = None,
    ) -> Any:
        """
        Backward-compatible alias.
        """

        return self.add_memory(
            messages=text,
            user_id=user_id,
            metadata=metadata,
        )

    def search(
        self,
        query: str,
        user_id: str,
        limit: int = 5,
    ) -> Any:
        """
        Backward-compatible alias.
        """
        if self.memory is None:
            return []
        try:
            return self.memory.search(
                query,
                filters={"user_id": user_id},
                limit=limit,
           )
        except Exception as exc:
            raise RuntimeError(
                f"Mem0 search failed for user_id={user_id!r}: {exc}"
            ) from exc   

    def get_all(
        self,
        user_id: str,
    ) -> Any:
        """
        Backward-compatible alias.
        """

        return self.get_all_memory(
            "user_id": user_id,
        )