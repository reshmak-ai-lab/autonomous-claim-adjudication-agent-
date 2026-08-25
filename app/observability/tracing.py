"""
Local execution tracing.

Provides a lightweight trace system that records the execution
of claim-processing nodes.
"""

from __future__ import annotations

import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Generator, List, Optional


@dataclass
class TraceEvent:
    """
    Represents one execution event.
    """

    event_id: str
    trace_id: str
    event_name: str
    started_at: str
    completed_at: Optional[str] = None
    duration_ms: Optional[float] = None
    status: str = "running"
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


class TraceContext:
    """
    Collects execution events for one workflow run.
    """

    def __init__(
        self,
        trace_id: Optional[str] = None,
        claim_id: Optional[str] = None,
    ):

        self.trace_id = trace_id or str(uuid.uuid4())
        self.claim_id = claim_id

        self.events: List[TraceEvent] = []

        self.started_at = self._timestamp()
        self.completed_at: Optional[str] = None

    @staticmethod
    def _timestamp() -> str:
        return datetime.now(
            timezone.utc
        ).isoformat()

    @contextmanager
    def span(
        self,
        event_name: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Generator[TraceEvent, None, None]:
        """
        Trace one execution step.

        Example:

            with trace.span("fraud_detection"):
                fraud_engine.analyze(...)
        """

        event = TraceEvent(
            event_id=str(uuid.uuid4()),
            trace_id=self.trace_id,
            event_name=event_name,
            started_at=self._timestamp(),
            metadata=metadata or {},
        )

        self.events.append(event)

        start_time = time.perf_counter()

        try:

            yield event

            event.status = "success"

        except Exception as exc:

            event.status = "error"
            event.error = str(exc)

            raise

        finally:

            event.completed_at = self._timestamp()

            event.duration_ms = round(
                (time.perf_counter() - start_time) * 1000,
                3,
            )

    def complete(self) -> None:
        """
        Mark the complete workflow.
        """

        self.completed_at = self._timestamp()

    def add_event(
        self,
        event_name: str,
        status: str = "success",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> TraceEvent:
        """
        Add an already-completed event.
        """

        timestamp = self._timestamp()

        event = TraceEvent(
            event_id=str(uuid.uuid4()),
            trace_id=self.trace_id,
            event_name=event_name,
            started_at=timestamp,
            completed_at=timestamp,
            duration_ms=0.0,
            status=status,
            metadata=metadata or {},
        )

        self.events.append(event)

        return event

    def to_dict(self) -> Dict[str, Any]:

        return {
            "trace_id": self.trace_id,
            "claim_id": self.claim_id,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "event_count": len(self.events),
            "events": [
                {
                    "event_id": event.event_id,
                    "trace_id": event.trace_id,
                    "event_name": event.event_name,
                    "started_at": event.started_at,
                    "completed_at": event.completed_at,
                    "duration_ms": event.duration_ms,
                    "status": event.status,
                    "metadata": event.metadata,
                    "error": event.error,
                }
                for event in self.events
            ],
        }


# ---------------------------------------------------------------------------
# Simple tracer factory
# ---------------------------------------------------------------------------

def get_tracer(
    claim_id: Optional[str] = None,
) -> TraceContext:

    return TraceContext(
        claim_id=claim_id,
    )