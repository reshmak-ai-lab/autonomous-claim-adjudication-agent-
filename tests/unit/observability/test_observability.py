from app.observability import (
    MetricsCollector,
    TraceContext,
    WorkflowCallback,
)


def test_trace_context():

    trace = TraceContext(
        claim_id="CLM-TEST-001"
    )

    with trace.span(
        "policy_retrieval",
        metadata={
            "documents": 3
        },
    ):
        pass

    trace.complete()

    result = trace.to_dict()

    assert result["claim_id"] == "CLM-TEST-001"
    assert result["event_count"] == 1
    assert result["events"][0]["status"] == "success"


def test_metrics_collector():

    collector = MetricsCollector()

    collector.increment(
        "claims.processed"
    )

    collector.increment(
        "claims.processed"
    )

    snapshot = collector.snapshot()

    assert (
        snapshot["counters"]["claims.processed"]
        == 2
    )


def test_workflow_callback():

    trace = TraceContext(
        claim_id="CLM-TEST-002"
    )

    collector = MetricsCollector()

    callback = WorkflowCallback(
        trace=trace,
        metrics_collector=collector,
    )

    callback.on_node_start(
        "fraud_detection"
    )

    callback.on_node_complete(
        "fraud_detection",
        metadata={
            "fraud_score": 0.25
        },
    )

    result = trace.to_dict()

    assert result["event_count"] == 2

    snapshot = collector.snapshot()

    assert (
        snapshot["counters"][
            "workflow.node.fraud_detection.started"
        ]
        == 1
    )