"""
Serve metrics queue metadata endpoints when in daemon mode.
"""


from http import HTTPStatus

import logging

from flask import Flask
from flask.typing import ResponseReturnValue

from orchidarium.runtime.queue import get_queue_summary

log = logging.getLogger(__name__)


__all__ = [
    'create_queue_api',
]


def create_queue_api(app: Flask) -> None:
    """
    Create queue metadata endpoints for a Flask app instance.

    Args:
        app (Flask): Flask app instance.
    """

    log.debug(f'Creating queue API')

    @app.get('/metrics/queue/backlog')
    def queue_backlog() -> ResponseReturnValue:
        """
        Return queue backlog and rolling activity summary.

        The response is the latest metrics-process queue summary snapshot. It reports aggregate backlog across
        all publisher queues, plus a per-publisher breakdown keyed by publisher name.

        Returns:
            ResponseReturnValue: JSON payload and HTTP 200 status. The payload has schema like

            {
                "current_backlog": 0,
                "total_current_backlog": 0,
                "publisher_count": 1,
                "window_seconds": 3600,
                "sample_count": 0,
                "min_queue_length": 0,
                "max_queue_length": 0,
                "average_queue_length": 0.0,
                "enqueued": 0,
                "dequeued": 0,
                "last_enqueued_at": "ISO-8601 timestamp | null",
                "last_dequeued_at": "ISO-8601 timestamp | null",
                "queues": {
                    "influxdb": {
                        "current_backlog": 0,
                        "window_seconds": 3600,
                        "sample_count": 0,
                        "min_queue_length": 0,
                        "max_queue_length": 0,
                        "average_queue_length": 0.0,
                        "enqueued": 0,
                        "dequeued": 0,
                        "last_enqueued_at": "ISO-8601 timestamp | null",
                        "last_dequeued_at": "ISO-8601 timestamp | null"
                    }
                }
            }
        """
        return (
            get_queue_summary(),
            HTTPStatus.OK
        )
