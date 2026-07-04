"""
Create metrics API endpoints.
"""


from flask import Flask

from orchidarium.api.metrics.queue import create_queue_api
from orchidarium.api.metrics.sensors import create_sensor_api


__all__ = [
    'create_metrics_api',
    'create_queue_api',
    'create_sensor_api'
]


def create_metrics_api(app: Flask) -> None:
    """
    Create metrics endpoints for a Flask app instance.

    Args:
        app (Flask): Flask app instance.
    """
    create_queue_api(app)
    create_sensor_api(app)
