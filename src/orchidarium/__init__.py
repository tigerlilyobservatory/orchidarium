import logging
import os
import sys

from typing import Dict


log = logging.getLogger(__name__)

env: Dict[str, str]  = {
    'INFLUXDB_HOST':     os.getenv('INFLUXDB_HOST', 'influxdb:8086'),
    'INFLUXDB_TOKEN':    os.getenv('INFLUXDB_TOKEN', ''),
    'INFLUXDB_ORG':      os.getenv('INFLUXDB_ORG', 'orchidarium'),
    'INFLUXDB_DATABASE': os.getenv('INFLUXDB_DATABASE', 'orchidarium'),
    'INTERVAL':          os.getenv('INTERVAL', '60')
}

try:
    int(env['INTERVAL'])
except ValueError as e:
    log.error(e)
    sys.exit(1)