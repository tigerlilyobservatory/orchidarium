"""
Read temperature and humidity data from USB sensor in my Orchidarium.
"""


from __future__ import annotations

import logging
import sys

from concurrent.futures import ThreadPoolExecutor, as_completed
from orchidarium.publishers.influxdb import InfluxDBPublisher
from orchidarium.api.health import HealthCheck
from orchidarium.sensors.soil import SoilSensor
from orchidarium.sensors.humidity import HumiditySensor
from orchidarium import env


log = logging.getLogger(__name__)


## Main


def main() -> int:
    publisher = InfluxDBPublisher()
    publisher.connect()

    with ThreadPoolExecutor(max_workers=3) as pool:
        pool.submit()
        SoilSensor().publish(
            publisher
        )

        HumiditySensor().publish(
            publisher
        )

        HealthCheck(port=int(env['HEALTHCHECK_PORT']))

        for future in as_completed(pool):



def cli() -> None:
    sys.exit(
        main()
    )


if __name__ == '__main__':
    cli()