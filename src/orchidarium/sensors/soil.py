"""
Define a soil sensor type that encapsulates the logic for interacting with our soil sensor.
"""


from ._base import Sensor
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from orchidarium.publishers._base import Publisher


class SoilSensor(Sensor):
    def collect(self) -> bool:
        ...

    def publish(self, publisher: Publisher) -> bool:
        ...