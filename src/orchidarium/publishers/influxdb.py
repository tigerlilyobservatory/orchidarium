"""
Provide an InfluxDB Publisher subclass to interact cleanly with the InfluxDB API to publish metrics.
"""


from __future__ import annotations

from . import Publisher
from influxdb_client_3 import InfluxDBClient
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
        self._client = InfluxDBClient(
            host=env['INFLUXDB_HOST'],
            org=env['INFLUXDB_ORG'],
            token=env['INFLUXDB_TOKEN'],
            database=env['INFLUXDB_DATABASE']
        )

        return bool(self._client)

    def __enter__(self) -> InfluxDBPublisher:
        self.connect()
        return self

    def __exit__(self) -> Any:
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