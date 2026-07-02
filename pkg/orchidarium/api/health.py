"""
Serve healthcheck endpoints when in daemon mode.
"""


from http import HTTPStatus

import logging

from flask import Flask
from flask.typing import ResponseReturnValue

from orchidarium.runtime.health import (
    get_hardware_process_health,
    get_thread_pool_health,
    is_hardware_process_healthy,
    is_thread_pool_healthy,
    is_thread_pool_ready
)
from orchidarium.runtime.queue import get_point_backlog_health, is_point_backlog_ready


log = logging.getLogger(__name__)


__all__ = [
    'create_healthcheck_api'
]


def _health_response(healthy: bool) -> ResponseReturnValue:
    """
    Build the shared health and readiness response payload.

    Args:
        healthy (bool): whether the endpoint should report success.

    Returns:
        ResponseReturnValue: JSON payload and HTTP status. The payload has schema like

        {
            "status": "OK | Failed",
            "hardware_process": {
                "status": "starting | running | healthy | failed",
                "process_name": "hardware",
                "last_heartbeat_at": "ISO-8601 timestamp | null",
                "heartbeat_timeout_seconds": 5.0,
                "heartbeat_age_seconds": 0.0,
                "last_error": "error detail | null"
            },
            "point_backlog": {
                "current_backlog": 0,
                "max_point_backlog": 1000,
                "ready": true
            },
            "thread_pool": {
                "status": "starting | running | healthy | failed",
                "expected_workers": 0,
                "completed_workers": 0,
                "failed_workers": 0,
                "last_run_successful": false,
                "successful_runs": 0,
                "last_error": "error detail | null"
            }
        }
    """
    return (
        {
            'status': 'OK' if healthy else 'Failed',
            'hardware_process': get_hardware_process_health(),
            'point_backlog': get_point_backlog_health(),
            'thread_pool': get_thread_pool_health()
        },
        HTTPStatus.OK if healthy else HTTPStatus.SERVICE_UNAVAILABLE
    )


def create_healthcheck_api(app: Flask) -> None:
    """
    Create a healthcheck API for a Flask app instance.

    Args:
        app (Flask): Flask app instance.
    """

    log.debug(f'Creating healthcheck API')

    @app.get('/health')
    def healthcheck() -> ResponseReturnValue:
        """
        Quick unauthenticated healthcheck endpoint.

        This endpoint reports process liveness. It returns HTTP 200 when the metrics thread pool is running or
        healthy, the hardware process has a recent heartbeat, and no sensor workers have failed. It returns HTTP
        503 with the same payload schema when those liveness checks fail. The point backlog is included for
        debugging context, but it does not decide the /health status.

        Returns:
            ResponseReturnValue: JSON payload and HTTP status. The payload has schema like

            {
                "status": "OK | Failed",
                "hardware_process": {
                    "status": "starting | running | healthy | failed",
                    "process_name": "hardware",
                    "last_heartbeat_at": "ISO-8601 timestamp | null",
                    "heartbeat_timeout_seconds": 5.0,
                    "heartbeat_age_seconds": 0.0,
                    "last_error": "error detail | null"
                },
                "point_backlog": {
                    "current_backlog": 0,
                    "max_point_backlog": 1000,
                    "ready": true
                },
                "thread_pool": {
                    "status": "starting | running | healthy | failed",
                    "expected_workers": 0,
                    "completed_workers": 0,
                    "failed_workers": 0,
                    "last_run_successful": false,
                    "successful_runs": 0,
                    "last_error": "error detail | null"
                }
            }
        """
        return _health_response(
            is_thread_pool_healthy()
            and is_hardware_process_healthy()
        )

    @app.get('/ready')
    def readiness() -> ResponseReturnValue:
        """
        Quick unauthenticated readiness endpoint.

        This endpoint reports whether the container should receive work. It returns HTTP 200 only when the
        metrics thread pool is ready, the hardware process has a recent heartbeat, and the largest publisher
        queue backlog is below MAX_POINT_BACKLOG. It returns HTTP 503 with the same payload schema otherwise.

        Returns:
            ResponseReturnValue: JSON payload and HTTP status. The payload has schema like

            {
                "status": "OK | Failed",
                "hardware_process": {
                    "status": "starting | running | healthy | failed",
                    "process_name": "hardware",
                    "last_heartbeat_at": "ISO-8601 timestamp | null",
                    "heartbeat_timeout_seconds": 5.0,
                    "heartbeat_age_seconds": 0.0,
                    "last_error": "error detail | null"
                },
                "point_backlog": {
                    "current_backlog": 0,
                    "max_point_backlog": 1000,
                    "ready": true
                },
                "thread_pool": {
                    "status": "starting | running | healthy | failed",
                    "expected_workers": 0,
                    "completed_workers": 0,
                    "failed_workers": 0,
                    "last_run_successful": false,
                    "successful_runs": 0,
                    "last_error": "error detail | null"
                }
            }
        """
        return _health_response(
            is_thread_pool_ready()
            and is_hardware_process_healthy()
            and is_point_backlog_ready()
        )
