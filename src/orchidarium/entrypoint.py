"""
Read temperature and humidity data from USB sensor in my Orchidarium.
"""


from __future__ import annotations

import logging
import sys
import re

from time import sleep
from usb.core import find
from orchidarium import env
from orchidarium.lib.bus import InterfaceClaim, read
from orchidarium.sensors.soil import SoilSensor
from orchidarium.sensors.humidity import HumiditySensor



log = logging.getLogger(__name__)


## Main


def main() -> int:

    SoilSensor().publish()
    HumiditySensor().publish()

    device = find(
        idVendor=int(
            env['USB_VENDOR_ID'],
            base=16
        ),
        idProduct=int(
            env['USB_PRODUCT_ID'],
            base=16
        )
    )

    if device is None:
        log.error(f'USB device with idVendor "{env["USB_VENDOR_ID"]}" and idProduct "{env["USB_PRODUCT_ID"]}" not found, exiting.')
        return 1

    while True:
        with InterfaceClaim(device, detach=True):
            _match: re.Pattern = re.compile(r'T: [0-9]+.[0-9]+, RH: [0-9]+.[0-9]+\r\n')
            _extract_temperature: re.Pattern = re.compile(r'(?<=T: )[0-9]+.[0-9]+(?=,)')
            _extract_relative_humidity: re.Pattern = re.compile(r'(?<=RH: )[0-9]+.[0-9]+(?=\r\n)')

            if re.match(_match, (_res := read(device[0][(0,0)][0], device).decode('utf-8', errors='replace'))):
                print(_res)
                temperature = float(re.search(_extract_temperature, _res).group())
                print(temperature)
                humidity = float(re.search(_extract_relative_humidity, _res).group())
                print(humidity)
                return 0
        print(_res)
        sleep(5)


def cli() -> None:
    sys.exit(
        main()
    )


if __name__ == '__main__':
    cli()