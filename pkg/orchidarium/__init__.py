import logging
import os
import sys

from orchidarium.runtime.config import configured_env_value

log = logging.getLogger(__name__)

_healthcheck_port = os.getenv('HEALTHCHECK_PORT', '8085')
_readiness_url = f'http://127.0.0.1:{_healthcheck_port}/ready'

env: dict[str, str]  = {
    'DEBUG':                  os.getenv('DEBUG',                                              ''),
    'INFLUXDB_HOST':          os.getenv('INFLUXDB_HOST',                         'influxdb:8086'),
    'INFLUXDB_TOKEN':         os.getenv('INFLUXDB_TOKEN',                                     ''),
    'INFLUXDB_ORG':           os.getenv('INFLUXDB_ORG',                            'orchidarium'),
    'INFLUXDB_DATABASE':      os.getenv('INFLUXDB_DATABASE',                       'orchidarium'),
    'INTERVAL':               configured_env_value('INTERVAL', os.getenv('INTERVAL',        '60')),
    'MAX_POINT_BACKLOG':      configured_env_value('MAX_POINT_BACKLOG', os.getenv('MAX_POINT_BACKLOG', '1000')),
    'ORCHIDARIUM_MONITORING_URL': os.getenv('ORCHIDARIUM_MONITORING_URL', 'https://grafana:3000'),
    'ORCHIDARIUM_READINESS_URL': os.getenv('ORCHIDARIUM_READINESS_URL', _readiness_url),
    'ORCHIDARIUM_RUNTIME_DIR': os.getenv('ORCHIDARIUM_RUNTIME_DIR',          '/tmp/orchidarium'),
    'TMPDIR':                 os.getenv('TMPDIR',                            '/tmp/orchidarium'),
    'HEALTHCHECK_PORT':       _healthcheck_port
}

try:
    int(env['INTERVAL'])
    int(env['HEALTHCHECK_PORT'])
    int(env['MAX_POINT_BACKLOG'])

    if int(env['INTERVAL']) < 5:
        raise ValueError('INTERVAL must be at least 5 seconds')

    if int(env['MAX_POINT_BACKLOG']) < 0:
        raise ValueError('MAX_POINT_BACKLOG must be greater than or equal to 0')
except ValueError as e:
    log.error(e)
    sys.exit(1)
