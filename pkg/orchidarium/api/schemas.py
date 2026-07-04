"""
Define typed API response payloads.
"""


from __future__ import annotations

from attrs import define, field


__all__ = [
    'ActiveSensorsResponse',
    'HealthResponse',
    'HardwareProcessHealthResponse',
    'PointBacklogHealthResponse',
    'QueueActivitySummaryResponse',
    'QueueRegistryActivitySummaryResponse',
    'ThreadPoolHealthResponse'
]


@define(frozen=True)
class HardwareProcessHealthResponse:
    """
    Hardware-process health fields.
    """

    status: str
    process_name: str
    last_heartbeat_at: str | None = None
    heartbeat_timeout_seconds: float = 5.0
    heartbeat_age_seconds: float | None = None
    last_error: str | None = None


@define(frozen=True)
class PointBacklogHealthResponse:
    """
    Publisher queue backlog readiness fields.
    """

    current_backlog: int
    max_point_backlog: int
    ready: bool


@define(frozen=True)
class ThreadPoolHealthResponse:
    """
    Metrics thread-pool health fields.
    """

    status: str
    expected_workers: int
    completed_workers: int
    failed_workers: int
    last_run_successful: bool
    successful_runs: int
    last_error: str | None = None


@define(frozen=True)
class HealthResponse:
    """
    Combined health or readiness response.
    """

    status: str
    hardware_process: HardwareProcessHealthResponse
    point_backlog: PointBacklogHealthResponse
    thread_pool: ThreadPoolHealthResponse


@define(frozen=True)
class QueueActivitySummaryResponse:
    """
    Rolling activity summary for one publisher queue.
    """

    current_backlog: int
    window_seconds: int
    sample_count: int
    min_queue_length: int
    max_queue_length: int
    average_queue_length: float
    enqueued: int
    dequeued: int
    last_enqueued_at: str | None = None
    last_dequeued_at: str | None = None


@define(frozen=True)
class QueueRegistryActivitySummaryResponse:
    """
    Rolling activity summary across all publisher queues.
    """

    current_backlog: int
    total_current_backlog: int
    publisher_count: int
    window_seconds: int
    sample_count: int
    min_queue_length: int
    max_queue_length: int
    average_queue_length: float
    enqueued: int
    dequeued: int
    queues: dict[str, QueueActivitySummaryResponse] = field(factory=dict)
    last_enqueued_at: str | None = None
    last_dequeued_at: str | None = None


@define(frozen=True)
class ActiveSensorsResponse:
    """
    Active sensor-count response.
    """

    active_sensors: int
