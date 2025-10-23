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


def cli() -> None:
    sys.exit(
        main()
    )


if __name__ == '__main__':
    cli()