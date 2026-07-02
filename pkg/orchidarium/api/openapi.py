"""
Generate and serve the Orchidarium OpenAPI specification.
"""


from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from http import HTTPStatus
from importlib.metadata import PackageNotFoundError, version
from typing import Any, cast

import logging

from flask import Flask
from flask.typing import ResponseReturnValue
from pyopenapi.decorators import webmethod
from pyopenapi.generator import Generator
from pyopenapi.options import Options
from pyopenapi.specification import Info, Server
from strong_typing.serialization import object_to_json

from orchidarium import env
from orchidarium.api.schemas import (
    ActiveSensorsResponse,
    HardwareProcessHealthResponse,
    HealthResponse,
    PointBacklogHealthResponse,
    QueueActivitySummaryResponse,
    QueueRegistryActivitySummaryResponse,
    ThreadPoolHealthResponse
)


log = logging.getLogger(__name__)


__all__ = [
    'create_openapi_api',
    'generate_openapi_spec'
]


_HEALTHY_RESPONSE_EXAMPLE = HealthResponse(
    status='OK',
    hardware_process=HardwareProcessHealthResponse(
        status='healthy',
        process_name='hardware',
        last_heartbeat_at='2026-07-02T12:00:00+00:00',
        heartbeat_timeout_seconds=5.0,
        heartbeat_age_seconds=0.25,
        last_error=None
    ),
    point_backlog=PointBacklogHealthResponse(
        current_backlog=0,
        max_point_backlog=1000,
        ready=True
    ),
    thread_pool=ThreadPoolHealthResponse(
        status='healthy',
        expected_workers=3,
        completed_workers=3,
        failed_workers=0,
        last_run_successful=True,
        successful_runs=42,
        last_error=None
    )
)


_FAILED_RESPONSE_EXAMPLE = HealthResponse(
    status='Failed',
    hardware_process=HardwareProcessHealthResponse(
        status='failed',
        process_name='hardware',
        last_heartbeat_at='2026-07-02T12:00:00+00:00',
        heartbeat_timeout_seconds=5.0,
        heartbeat_age_seconds=12.5,
        last_error='Hardware heartbeat is stale'
    ),
    point_backlog=PointBacklogHealthResponse(
        current_backlog=1000,
        max_point_backlog=1000,
        ready=False
    ),
    thread_pool=ThreadPoolHealthResponse(
        status='failed',
        expected_workers=3,
        completed_workers=2,
        failed_workers=1,
        last_run_successful=False,
        successful_runs=42,
        last_error='Sensor "humidity" failed'
    )
)


_QUEUE_RESPONSE_EXAMPLE = QueueRegistryActivitySummaryResponse(
    current_backlog=0,
    total_current_backlog=0,
    publisher_count=1,
    window_seconds=3600,
    sample_count=12,
    min_queue_length=0,
    max_queue_length=4,
    average_queue_length=0.5,
    enqueued=6,
    dequeued=6,
    last_enqueued_at='2026-07-02T12:00:00+00:00',
    last_dequeued_at='2026-07-02T12:00:01+00:00',
    queues={
        'influxdb': QueueActivitySummaryResponse(
            current_backlog=0,
            window_seconds=3600,
            sample_count=12,
            min_queue_length=0,
            max_queue_length=4,
            average_queue_length=0.5,
            enqueued=6,
            dequeued=6,
            last_enqueued_at='2026-07-02T12:00:00+00:00',
            last_dequeued_at='2026-07-02T12:00:01+00:00'
        )
    }
)


class OrchidariumAPI:
    """
    Orchidarium daemon API.
    """

    @webmethod(route='/health', public=True, response_example=_HEALTHY_RESPONSE_EXAMPLE)
    def get_health(self) -> HealthResponse:
        """
        Return controller liveness.

        Returns:
            HealthResponse: liveness payload.
        """
        return _HEALTHY_RESPONSE_EXAMPLE

    @webmethod(route='/ready', public=True, response_example=_HEALTHY_RESPONSE_EXAMPLE)
    def get_ready(self) -> HealthResponse:
        """
        Return controller scheduler readiness.

        Returns:
            HealthResponse: readiness payload.
        """
        return _HEALTHY_RESPONSE_EXAMPLE

    @webmethod(route='/metrics/queue/backlog', public=True, response_example=_QUEUE_RESPONSE_EXAMPLE)
    def get_queue_backlog(self) -> QueueRegistryActivitySummaryResponse:
        """
        Return publisher queue backlog and rolling activity summaries.

        Returns:
            QueueRegistryActivitySummaryResponse: queue backlog and activity payload.
        """
        return _QUEUE_RESPONSE_EXAMPLE

    @webmethod(route='/metrics/sensors/active', public=True, response_example=ActiveSensorsResponse(active_sensors=3))
    def get_active_sensors(self) -> ActiveSensorsResponse:
        """
        Return the active sensor count.

        Returns:
            ActiveSensorsResponse: active sensor-count payload.
        """
        return ActiveSensorsResponse(active_sensors=3)


def _package_version() -> str:
    """
    Return the installed Orchidarium package version.

    Returns:
        str: installed package version, or the source-tree fallback version.
    """
    try:
        return version('orchidarium')
    except PackageNotFoundError:
        return '0.0.1'


def _set_error_response(spec: dict[str, Any], path: str, description: str) -> None:
    """
    Add the shared HTTP 503 response to an operation.

    Args:
        spec (dict[str, Any]): OpenAPI specification dictionary.
        path (str): OpenAPI path to update.
        description (str): response description.
    """
    response = deepcopy(spec['paths'][path]['get']['responses']['200'])
    response['description'] = description
    response['content']['application/json']['example'] = object_to_json(_FAILED_RESPONSE_EXAMPLE)
    spec['paths'][path]['get']['responses'][str(HTTPStatus.SERVICE_UNAVAILABLE.value)] = response


def _document_openapi_endpoint(spec: dict[str, Any]) -> None:
    """
    Add the OpenAPI document endpoint to its own specification.

    Args:
        spec (dict[str, Any]): OpenAPI specification dictionary.
    """
    spec['paths']['/openapi.json'] = {
        'get': {
            'tags': ['OpenAPI'],
            'summary': 'Return the OpenAPI specification.',
            'description': 'Returns the generated OpenAPI 3.1 document for the Orchidarium Flask API.',
            'parameters': [],
            'responses': {
                str(HTTPStatus.OK.value): {
                    'description': 'OpenAPI specification document.',
                    'content': {
                        'application/json': {
                            'schema': {
                                'type': 'object',
                                'additionalProperties': True
                            }
                        }
                    }
                }
            },
            'security': [],
            'deprecated': False
        }
    }
    spec.setdefault('tags', []).append(
        {
            'name': 'OpenAPI',
            'description': 'Generated OpenAPI specification endpoint.'
        }
    )


@lru_cache(maxsize=1)
def generate_openapi_spec() -> dict[str, Any]:
    """
    Generate the OpenAPI specification for the Flask API.

    Returns:
        dict[str, Any]: OpenAPI 3.1 specification document.
    """
    document = Generator(
        OrchidariumAPI,
        Options(
            server=Server(url=f'http://localhost:{env["HEALTHCHECK_PORT"]}'),
            info=Info(
                title='Orchidarium API',
                version=_package_version(),
                description='Runtime health, readiness, queue, and sensor metadata for Orchidarium.'
            ),
            extra_types={
                'Health': [
                    HealthResponse,
                    HardwareProcessHealthResponse,
                    PointBacklogHealthResponse,
                    ThreadPoolHealthResponse
                ],
                'Queues': [
                    QueueRegistryActivitySummaryResponse,
                    QueueActivitySummaryResponse
                ],
                'Sensors': [
                    ActiveSensorsResponse
                ]
            },
            captions={
                'Health': 'Health',
                'Queues': 'Queues',
                'Sensors': 'Sensors'
            }
        )
    ).generate()

    spec = cast(dict[str, Any], object_to_json(document))
    _set_error_response(spec, '/health', 'Controller liveness failed.')
    _set_error_response(spec, '/ready', 'Controller readiness failed.')
    _document_openapi_endpoint(spec)
    spec.pop('security', None)

    return spec


def create_openapi_api(app: Flask) -> None:
    """
    Create OpenAPI specification endpoints for a Flask app instance.

    Args:
        app (Flask): Flask app instance.
    """

    log.debug(f'Creating OpenAPI API')

    @app.get('/openapi.json')
    def openapi_spec() -> ResponseReturnValue:
        """
        Return the generated OpenAPI specification.

        Returns:
            ResponseReturnValue: OpenAPI 3.1 JSON document and HTTP 200 status.
        """
        return (
            generate_openapi_spec(),
            HTTPStatus.OK
        )
