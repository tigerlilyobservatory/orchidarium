"""
Read temperature and humidity data from USB sensor in my Orchidarium.
"""


from __future__ import annotations

import logging
import sys
import traceback

from time import sleep
from functools import partial
from concurrent.futures import ThreadPoolExecutor, as_completed
from orchidarium.publishers.influxdb import InfluxDBPublisher
from orchidarium.api import app
from orchidarium.sensors.soil import SoilSensor
from orchidarium.sensors.humidity import HumiditySensor
from orchidarium import env


log = logging.getLogger(__name__)


## Main


def daemon() -> int:
    publisher = InfluxDBPublisher()
    publisher.connect()

    try:
        while True:
            with ThreadPoolExecutor(max_workers=3, thread_name_prefix='orchidarium') as pool:
                threads = [
                    pool.submit(
                        partial(
                            SoilSensor().publish(publisher)
                        )
                    ),
                    pool.submit(
                        partial(
                            HumiditySensor().publish(publisher)
                        )
                    ),
                    pool.submit(
                        partial(
                            app.run,
                            port=int(env['HEALTHCHECK_PORT'])
                        )
                    )
                ]

                filtered_threads = [thread for thread in threads if thread is not None]

                for thread in as_completed(filtered_threads):
                    try:
                        thread.result()
                    except Exception:
                        log.error(f'Thread {thread} failed. Full traceback: {traceback.format_exc()}')

                        for _thread in filtered_threads:
                            if _thread is not thread:
                                log.debug(f'Terminating process {_thread}')
                                _thread.cancel()
                                log.debug(f'Process {_thread} terminated successfully')

                        _ret_code = 1
                        break
                else:
                    _ret_code = 0

            sleep(int(env['INTERVAL']))
    except Exception as e:
        _ret_code = 1
        log.error(e)

    return _ret_code


def cli() -> None:
    sys.exit(
        daemon()
    )


if __name__ == '__main__':
    cli()