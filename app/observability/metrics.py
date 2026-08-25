"""
Application metrics collector.

The implementation is intentionally lightweight and dependency-free.
It can later be replaced or extended with Prometheus/OpenTelemetry.
"""

from __future__ import annotations

import threading
import time
from collections import defaultdict
from typing import Any, Dict


class MetricsCollector:

    def __init__(self):

        self._lock = threading.Lock()

        self.counters = defaultdict(int)

        self.timers = defaultdict(list)

    # ------------------------------------------------------------------
    # Counters
    # ------------------------------------------------------------------

    def increment(
        self,
        metric: str,
        value: int = 1,
    ) -> None:

        with self._lock:
            self.counters[metric] += value

    # ------------------------------------------------------------------
    # Timing
    # ------------------------------------------------------------------

    def record_time(
        self,
        metric: str,
        duration_ms: float,
    ) -> None:

        with self._lock:
            self.timers[metric].append(
                float(duration_ms)
            )

    # ------------------------------------------------------------------
    # Context manager
    # ------------------------------------------------------------------

    def timer(self, metric: str):

        return _MetricTimer(
            collector=self,
            metric=metric,
        )

    # ------------------------------------------------------------------
    # Claim metrics
    # ------------------------------------------------------------------

    def record_claim(
        self,
        decision: str,
        fraud_detected: bool = False,
        processing_time_ms: float | None = None,
    ) -> None:

        self.increment("claims.processed")

        self.increment(
            f"claims.decision.{decision.lower()}"
        )

        if fraud_detected:
            self.increment(
                "claims.fraud_detected"
            )

        if processing_time_ms is not None:
            self.record_time(
                "claims.processing_time",
                processing_time_ms,
            )

    # ------------------------------------------------------------------
    # Snapshot
    # ------------------------------------------------------------------

    def snapshot(self) -> Dict[str, Any]:

        with self._lock:

            timer_stats = {}

            for metric, values in self.timers.items():

                if not values:
                    continue

                timer_stats[metric] = {
                    "count": len(values),
                    "total_ms": round(
                        sum(values),
                        3,
                    ),
                    "average_ms": round(
                        sum(values) / len(values),
                        3,
                    ),
                    "min_ms": round(
                        min(values),
                        3,
                    ),
                    "max_ms": round(
                        max(values),
                        3,
                    ),
                }

            return {
                "counters": dict(self.counters),
                "timers": timer_stats,
            }

    def reset(self) -> None:

        with self._lock:
            self.counters.clear()
            self.timers.clear()


class _MetricTimer:

    def __init__(
        self,
        collector: MetricsCollector,
        metric: str,
    ):

        self.collector = collector
        self.metric = metric
        self.start_time = 0.0

    def __enter__(self):

        self.start_time = time.perf_counter()

        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):

        duration_ms = (
            time.perf_counter()
            - self.start_time
        ) * 1000

        self.collector.record_time(
            self.metric,
            duration_ms,
        )


# Global collector for application-wide metrics.
metrics = MetricsCollector()