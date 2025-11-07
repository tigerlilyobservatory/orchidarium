"""
Read temperature and humidity data from USB sensor in my Orchidarium.
"""


from __future__ import annotations

import logging
import sys
import traceback

from typing import TYPE_CHECKING
from setproctitle import setproctitle
from time import sleep
from functools import partial
from threading import Thread
from concurrent.futures import ThreadPoolExecutor, as_completed
from orchidarium.publishers.influxdb import InfluxDBPublisher
from orchidarium.api import app
from orchidarium.sensors.soil import SoilSensor
from orchidarium.sensors.humidity import HumiditySensor
from orchidarium import env

if TYPE_CHECKING:
    from typing import List
    from concurrent.futures import Future


log = logging.getLogger(__name__)
logging.basicConfig(
    stream=sys.stdout,
    level=logging.DEBUG if env['DEBUG'] != '' else logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s'
)


## Main


def daemon() -> int:
    """
    Daemon loop.

    Returns:
        int: 0 if successful, 1 or another exit code, otherwise.
    """
    _ret_code = 0

    setproctitle('orchidarium')

    # Start the healthcheck and other APIs in a separate thread off our main process as a daemon thread.
    _main_process_daemon_threads: List[Thread] = [
        Thread(
            target=partial(
                app.run,
                port=int(env['HEALTHCHECK_PORT'])
            ),
            # Do not block upon start().
            daemon=True
        ),
    ]

    for _dthread in _main_process_daemon_threads:
        _dthread.start()

    try:
        while True:
            # Start as many threads as there are sensors.
            with ThreadPoolExecutor(max_workers=2, thread_name_prefix='orchidarium') as pool, InfluxDBPublisher() as publisher:
                # Build a list
                threads: List[Future] = [
                    pool.submit(
                        partial(
                            SoilSensor(),
                            publisher
                        )
                    ),
                    pool.submit(
                        partial(
                            HumiditySensor(),
                            publisher
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
                                log.debug(f'Terminating thread "{_thread}"')
                                _thread.cancel()
                                log.debug(f'Thread "{_thread}" terminated successfully')

                        _ret_code = 1
                        break
                else:
                    _ret_code = 0

            sleep(int(env['INTERVAL']))
    except Exception as e:
        _ret_code = 1
        log.error(e)

    for _dthread in _main_process_daemon_threads:
        _dthread.join(timeout=5)

    return _ret_code


def cli() -> None:
    sys.exit(
        daemon()
    )


if __name__ == '__main__':
    cli()