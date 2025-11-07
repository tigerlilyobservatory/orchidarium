"""
Provide an InfluxDB Publisher subclass to interact cleanly with the InfluxDB API to publish metrics.
"""


from __future__ import annotations

from . import Publisher
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from orchidarium import env
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, List


__all__ = [
    'InfluxDBPublisher'
]


class InfluxDBPublisher(Publisher):
    """
    An interface for managing connections to, as well as submitting data to, an InfluxDB instance.
    """

    def __init__(self):
        self._client: Any = None

    def connect(self) -> bool:
        # Guard against re-opening the connection.
        if not self._client:
            self._client = InfluxDBClient(
                url=env["INFLUXDB_HOST"],
                org=env['INFLUXDB_ORG'],
                token=env['INFLUXDB_TOKEN'],
                database=env['INFLUXDB_DATABASE']
            )

        return bool(self._client)

    def __enter__(self) -> InfluxDBPublisher:
        self.connect()
        return self

    def __exit__(self, *args: Any) -> Any:
        self._client.close()

    def publish_datapoint(self, datum: Any) -> bool:
        """


        Args:
            datum (Any): _description_

        Returns:
            bool: _description_
        """
        return True

    def publish_datapoints(self, data: List[Any]) -> bool:
        """


        Args:
            data (List[Any]): _description_

        Returns:
            bool: _description_
        """
        return True