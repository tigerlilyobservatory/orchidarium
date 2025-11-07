from __future__ import annotations

import re
import logging

from time import sleep
from usb.core import find
from orchidarium import env
from orchidarium.sensors import Sensor
from orchidarium.lib.bus import InterfaceClaim, read
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from orchidarium.publishers import Publisher


log = logging.getLogger(__name__)


class HumiditySensor(Sensor):

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

            self._collection = False
            self.cache()

            return False

        with InterfaceClaim(device, detach=True):
            _match: re.Pattern = re.compile(r'')
            _extract_temperature: re.Pattern = re.compile(r'(?<=T: )[0-9]+.[0-9]+(?=,)')

            if re.match(_match, (_res := read(device[0][(0,0)][0], device).decode('utf-8', errors='replace'))):
                log.info(_res)

                _search = re.search(_extract_temperature, _res)

                if _search:
                    temperature = float(_search.group(0))
                    log.info(temperature)

                    self._collection = True
                    self.cache()

                    return True
                else:
                    log.error(f'Could not retrieve temperature')

        self._collection = False
        self.cache()

        return False

    def publish(self, publisher: Publisher) -> bool:
        ...
        self._publication = True
        self.cache()
        return True