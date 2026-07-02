"""
Serve sensor metadata endpoints when in daemon mode.
"""


from http import HTTPStatus

import logging

from cattrs import unstructure
from flask import Flask
from flask.typing import ResponseReturnValue

from orchidarium.api.schemas import ActiveSensorsResponse
from orchidarium.sensors import sensor_count

log = logging.getLogger(__name__)


__all__ = [
    'create_sensor_api',
]


def create_sensor_api(app: Flask) -> None:
    """
    Create sensor metadata endpoints for a Flask app instance.

    Args:
        app (Flask): Flask app instance.
    """

    log.debug(f'Creating sensor API')

    @app.get('/sensors/active')
    def active_sensors() -> ResponseReturnValue:
        """
        Return the number of active sensor types.

        Active sensors are discovered sensor classes that are currently enabled.

        Returns:
            ResponseReturnValue: JSON payload and HTTP 200 status. The payload has schema like

            {
                "active_sensors": 0
            }
        """
        return (
            unstructure(
                ActiveSensorsResponse(
                    active_sensors=sensor_count()
                )
            ),
            HTTPStatus.OK
        )
