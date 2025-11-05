from __future__ import annotations

import json
import os
import logging

from orchidarium import env
from cachetools import TTLCache
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict


log = logging.getLogger(__name__)


__all__ = [
    'write_json',
    'read_json',
    'cached_read_json'
]


def write_json(data: dict, path: str) -> None:
    """
    Write a dictionary to a JSON file.

    Args:
        data (dict): the dictionary to write.
        path (str): the path to write the file to.
    """
    path_e = os.path.expandvars(path)

    try:
        with open(path_e, 'w', encoding='utf-8') as f:
            log.debug(f'Writing JSON to file: {path_e}')
            json.dump(data, f)
    except (FileNotFoundError, PermissionError) as msg:
        log.error(f'Failed to write JSON file, received: {msg}')
    except OSError as msg:
        log.error(f'Failed to write JSON file {path_e}, received: {msg}. Check your path and permissions')


def read_json(path: str) -> Dict | None:
    """
    Read a JSON file and return the data as a dictionary.

    Args:
        path (str): the path to the JSON file.

    Returns:
        dict | None: the data from the JSON file, or None if the file does not exist.
    """
    try:
        if Path(path).exists():
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    except (FileNotFoundError, PermissionError) as msg:
        log.error(f'Failed to read JSON file, received: {msg}')
        return None


cache = TTLCache(
    maxsize=len(list(Path(env['HEALTHCHECK_CACHE_PATH']).iterdir())),
    ttl=int(env['HEALTHCHECK_CACHE_TTL'])
)


def cached_read_json(path: str) -> Dict | None:
    """
    Same function as 'read_json', the reads from disk are cached for the interval, however.
    """
    try:
        return cache[path]
    except KeyError as e:
        _json = read_json(path)
        cache[path] = _json
        return _json