"""
Configure Orchidarium logging.
"""


from __future__ import annotations

import logging
import sys

from typing import Final

from orchidarium import env


_banner_logged = False


_BANNER: Final[str] = r"""
   ___           _     _     _            _
  / _ \ _ __ ___| |__ (_) __| | __ _ _ __(_)_   _ _ __ ___
 | | | | '__/ __| '_ \| |/ _` |/ _` | '__| | | | | '_ ` _ \
 | |_| | | | (__| | | | | (_| | (_| | |  | | |_| | | | | | |
  \___/|_|  \___|_| |_|_|\__,_|\__,_|_|  |_|\__,_|_| |_| |_|

                    Tiger Lily Plants LLC.
                  https://tiger-lily-plants.com
"""


def _debug_enabled(value: str) -> bool:
    """
    Return whether a string value enables debug logging.

    Args:
        value (str): configured debug value.

    Returns:
        bool: True when debug logging should be enabled.
    """
    return value.strip().lower() in {'1', 'true', 'yes', 'on', 'debug'}


def _log_level() -> int:
    """
    Return the configured logging level.

    Returns:
        int: Python logging level.
    """
    return logging.DEBUG if _debug_enabled(env['DEBUG']) else logging.INFO


def _log_startup_preamble(level: int) -> None:
    """
    Log the process startup banner and legal notice once.

    Args:
        level (int): active Python logging level.
    """
    global _banner_logged

    if _banner_logged:
        return

    _banner_logged = True

    log = logging.getLogger(__name__)
    sys.stdout.write(_BANNER)
    sys.stdout.flush()
    log.info(f'Log level: {logging.getLevelName(level)}')
    log.info('Code copyright: Tiger Lily Plants LLC.')


def configure_logging() -> None:
    """
    Configure process logging from the current environment.
    """
    level = _log_level()

    logging.basicConfig(
        stream=sys.stdout,
        level=level,
        format='%(asctime)s | %(levelname)s | %(name)s | %(message)s'
    )
    _log_startup_preamble(level)
