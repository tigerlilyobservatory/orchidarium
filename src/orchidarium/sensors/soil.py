"""
Define a soil sensor type that encapsulates the logic for interacting with our soil sensor.
"""


import logging
import re

from time import sleep
from usb.core import find
from ._base import Sensor
from orchidarium.lib.bus import InterfaceClaim, read
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from orchidarium.publishers._base import Publisher


log = logging.getLogger(__name__)


class SoilSensor(Sensor):
    @property
    def temperature(self) -> float:
        return self._temperature

    @temperature.setter
    def temperature(self, value: float) -> None:
        self._temperature =

    def collect(self) -> bool:
        device = find(
            idVendor=int(
                '0x0487',
                base=16
            ),
            idProduct=int(
                '0x0007',
                base=16
            )
        )

        if device is None:
            log.error(f'USB device with idVendor "{env["USB_VENDOR_ID"]}" and idProduct "{env["USB_PRODUCT_ID"]}" not found, exiting.')
            return False

        while True:
            with InterfaceClaim(device, detach=True):
                _match: re.Pattern = re.compile(r'')
                _extract_temperature: re.Pattern = re.compile(r'(?<=T: )[0-9]+.[0-9]+(?=,)')

                if re.match(_match, (_res := read(device[0][(0,0)][0], device).decode('utf-8', errors='replace'))):
                    log.info(_res)
                    temperature = float(re.search(_extract_temperature, _res).group())
                    log.info(temperature)
                    return True
            print(_res)
            sleep(5)

    def publish(self, publisher: Publisher) -> bool:
        ...