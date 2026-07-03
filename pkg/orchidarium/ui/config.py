"""
Expose Orchidarium configuration to the QML UI.
"""


from __future__ import annotations

import logging

from PySide6.QtCore import QObject, Property, Signal, Slot

from orchidarium import env
from orchidarium.runtime.config import update_state


log = logging.getLogger(__name__)


_MIN_INTERVAL_SECONDS = 5
_MIN_MAX_POINT_BACKLOG = 0


def _coerce_config_int(value: object, minimum: int, fallback: int) -> int:
    """
    Coerce a UI configuration value to an integer with a minimum.

    Args:
        value (object): value supplied by the UI or environment.
        minimum (int): lowest allowed value.
        fallback (int): value to keep when coercion fails.

    Returns:
        int: coerced integer value.
    """
    try:
        result = int(str(value).strip())
    except (TypeError, ValueError):
        return fallback

    return max(minimum, result)


class Config(QObject):
    relayNamesChanged = Signal()
    fullscreenChanged = Signal()
    relayCountChanged = Signal()
    intervalSecondsChanged = Signal()
    maxPointBacklogChanged = Signal()
    monitoringUrlChanged = Signal()
    readinessUrlChanged = Signal()

    def __init__(self, fullscreen: bool = False, relay_count: int = 4, relay_names: dict[int, str] | None = None):
        super().__init__()
        self._fullscreen = fullscreen
        self._relay_count = relay_count
        self._interval_seconds = _coerce_config_int(env['INTERVAL'], _MIN_INTERVAL_SECONDS, 60)
        self._max_point_backlog = _coerce_config_int(env['MAX_POINT_BACKLOG'], _MIN_MAX_POINT_BACKLOG, 1000)

        if relay_names is None:
            self._relay_names = {}
        else:
            self._relay_names = relay_names

    @Property(bool, notify=fullscreenChanged)
    def fullscreen(self) -> bool:
        return self._fullscreen

    @Property(int, notify=relayCountChanged)
    def relayCount(self) -> int:
        return self._relay_count

    @Property(str, notify=intervalSecondsChanged)
    def intervalSeconds(self) -> str:
        return str(self._interval_seconds)

    @Property(str, notify=maxPointBacklogChanged)
    def maxPointBacklog(self) -> str:
        return str(self._max_point_backlog)

    @Property(str, notify=monitoringUrlChanged)
    def monitoringUrl(self) -> str:
        return env['ORCHIDARIUM_MONITORING_URL']

    @Property(str, notify=readinessUrlChanged)
    def readinessUrl(self) -> str:
        return env['ORCHIDARIUM_READINESS_URL']

    @Slot(int, result=str)
    def relayName(self, index: int) -> str:
        return self._relay_names.get(index, f"Relay {index + 1}")

    @Slot(int, str)
    def setRelayName(self, index: int, name: str) -> None:
        self._relay_names[index] = name
        self.relayNamesChanged.emit()

    @Slot(str)
    def setIntervalSeconds(self, value: str) -> None:
        """
        Persist the collection interval configured from the UI.

        Args:
            value (str): requested collection interval in seconds.
        """
        interval_seconds = _coerce_config_int(value, _MIN_INTERVAL_SECONDS, self._interval_seconds)
        changed = interval_seconds != self._interval_seconds

        self._interval_seconds = interval_seconds
        self._persist_runtime_config()

        if changed:
            self.intervalSecondsChanged.emit()

    @Slot(str)
    def setMaxPointBacklog(self, value: str) -> None:
        """
        Persist the maximum metric point backlog configured from the UI.

        Args:
            value (str): requested maximum backlog. Zero means no configured maximum.
        """
        max_point_backlog = _coerce_config_int(value, _MIN_MAX_POINT_BACKLOG, self._max_point_backlog)
        changed = max_point_backlog != self._max_point_backlog

        self._max_point_backlog = max_point_backlog
        self._persist_runtime_config()

        if changed:
            self.maxPointBacklogChanged.emit()

    def _persist_runtime_config(self) -> None:
        env['INTERVAL'] = str(self._interval_seconds)
        env['MAX_POINT_BACKLOG'] = str(self._max_point_backlog)

        try:
            update_state(
                INTERVAL=env['INTERVAL'],
                MAX_POINT_BACKLOG=env['MAX_POINT_BACKLOG']
            )
        except OSError:
            log.exception('Failed to persist UI runtime configuration')
