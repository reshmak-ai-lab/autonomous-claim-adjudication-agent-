"""
Workflow callbacks.

Callbacks allow the claim workflow to report:
- Node start
- Node completion
- Node failure
- Claim completion
"""

from __future__ import annotations

import time
from typing import Any, Optional

from .metrics import MetricsCollector, metrics
from .tracing import TraceContext


class WorkflowCallback:

    def __init__(
        self,
        trace: Optional[TraceContext] = None,
        metrics_collector: Optional[MetricsCollector] = None,
    ):

        self.trace = trace
        self.metrics = metrics_collector or metrics

        self._node_start_times: Dict[str, float] = {}

    # ------------------------------------------------------------------
    # Node started
    # ------------------------------------------------------------------

    def on_node_start(
        self,
        node_name: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:

        self._node_start_times[node_name] = (
            time.perf_counter()
        )

        self.metrics.increment(
            f"workflow.node.{node_name}.started"
        )

        if self.trace:

            self.trace.add_event(
                event_name=f"{node_name}.started",
                metadata=metadata or {},
            )

    # ------------------------------------------------------------------
    # Node completed
    # ------------------------------------------------------------------

    def on_node_complete(
        self,
        node_name: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:

        start_time = self._node_start_times.pop(
            node_name,
            None,
        )

        duration_ms = None

        if start_time is not None:

            duration_ms = (
                time.perf_counter()
                - start_time
            ) * 1000

            self.metrics.record_time(
                f"workflow.node.{node_name}",
                duration_ms,
            )

        self.metrics.increment(
            f"workflow.node.{node_name}.completed"
        )

        event_metadata = metadata or {}

        if duration_ms is not None:
            event_metadata = {
                **event_metadata,
                "duration_ms": round(
                    duration_ms,
                    3,
                ),
            }

        if self.trace:

            self.trace.add_event(
                event_name=f"{node_name}.completed",
                metadata=event_metadata,
            )

    # ------------------------------------------------------------------
    # Node failed
    # ------------------------------------------------------------------

    def on_node_error(
        self,
        node_name: str,
        error: Exception,
    ) -> None:

        self.metrics.increment(
            f"workflow.node.{node_name}.errors"
        )

        if self.trace:

            self.trace.add_event(
                event_name=f"{node_name}.failed",
                status="error",
                metadata={
                    "error": str(error),
                },
            )

    # ------------------------------------------------------------------
    # Claim completed
    # ------------------------------------------------------------------

    def on_claim_complete(
        self,
        decision: str,
        fraud_detected: bool = False,
        processing_time_ms: Optional[float] = None,
    ) -> None:

        self.metrics.record_claim(
            decision=decision,
            fraud_detected=fraud_detected,
            processing_time_ms=processing_time_ms,
        )

        if self.trace:

            self.trace.add_event(
                event_name="claim.completed",
                metadata={
                    "decision": decision,
                    "fraud_detected": fraud_detected,
                    "processing_time_ms": processing_time_ms,
                },
            )