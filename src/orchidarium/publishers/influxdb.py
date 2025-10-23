"""
Provide an InfluxDB Publisher subclass to interact cleanly with the InfluxDB API to publish metrics.
"""


from __future__ import annotations

from ._base import Publisher
from influxdb_client_3 import InfluxDBClient3
from orchidarium import env
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any


__all__ = [
    'InfluxDBPublisher'
]


class InfluxDBPublisher(Publisher):
    def __init__(self):
        self._client = None

    def connect(self) -> bool:
        self._client = InfluxDBClient3(
            host=env['INFLUXDB_HOST'],
            org=env['INFLUXDB_ORG'],
            token=env['INFLUXDB_TOKEN'],
            database=env['INFLUXDB_DATABASE']
        )

        return bool(self._client)

    def __enter__(self) -> InfluxDBPublisher:
        self.connect()

    def __exit__(self) -> Any:
        self._client.close()