"""
Read and write persisted Orchidarium UI configuration state.
"""


from __future__ import annotations

import json
import os
import tempfile

from contextlib import contextmanager
from json import JSONDecodeError
from pathlib import Path
from threading import Lock
from time import monotonic, time
from typing import TYPE_CHECKING

from attrs import define, field

if TYPE_CHECKING:
    from collections.abc import Iterator
    from typing import Any, Final, Mapping


STATE_ENV_VAR: Final[str] = 'ORCHIDARIUM_STATE_PATH'
DEFAULT_STATE_PATH: Final[Path] = Path(os.getenv(STATE_ENV_VAR, '/opt/orchidarium/config/state.json'))
STATE_FIELD_NAMES: Final[tuple[str, ...]] = (
    'INTERVAL',
    'MAX_POINT_BACKLOG',
)
STATE_FIELD_ALIASES: Final[dict[str, tuple[str, ...]]] = {
    'INTERVAL': ('INTERVAL', 'interval'),
    'MAX_POINT_BACKLOG': ('MAX_POINT_BACKLOG', 'max_point_backlog', 'maxPointBacklog'),
}
STATE_FIELD_MINIMUMS: Final[dict[str, int]] = {
    'INTERVAL': 5,
    'MAX_POINT_BACKLOG': 0,
}
_STATE_CACHE_TTL_SECONDS: Final[float] = 1.0
_state_cache_lock = Lock()


def _state_path(path: Path | str | None = None) -> Path:
    """
    Return the configured state file path.

    Args:
        path (Path | str | None): optional path override.

    Returns:
        Path: resolved state file path.
    """
    if path is not None:
        return Path(path)

    return Path(os.getenv(STATE_ENV_VAR, str(DEFAULT_STATE_PATH)))


def _coerce_optional_int(value: object, field_name: str) -> int | None:
    """
    Coerce a state value to an optional integer.

    Args:
        value (object): value to coerce.
        field_name (str): canonical state field name.

    Returns:
        int | None: coerced integer, or None when unavailable.
    """
    if value is None:
        return None

    if isinstance(value, str):
        value = value.strip()

        if value == '':
            return None

    try:
        result = int(value)
    except (TypeError, ValueError):
        return None

    if result < STATE_FIELD_MINIMUMS[field_name]:
        return None

    return result


def _optional_interval(value: object) -> int | None:
    return _coerce_optional_int(value, 'INTERVAL')


def _optional_max_point_backlog(value: object) -> int | None:
    return _coerce_optional_int(value, 'MAX_POINT_BACKLOG')


def _first_state_value(data: Mapping[str, object], field_name: str) -> object | None:
    for alias in STATE_FIELD_ALIASES[field_name]:
        if alias in data:
            return data[alias]

    return None


@define(frozen=True)
class UIState:
    """
    Persisted user-defined UI configuration.
    """

    interval: int | None = field(default=None, converter=_optional_interval)
    max_point_backlog: int | None = field(default=None, converter=_optional_max_point_backlog)

    @classmethod
    def from_mapping(cls, data: Mapping[str, object]) -> UIState:
        """
        Build state from a JSON mapping.

        Args:
            data (Mapping[str, object]): raw JSON state mapping.

        Returns:
            UIState: coerced UI state.
        """
        return cls(
            interval=_first_state_value(data, 'INTERVAL'),
            max_point_backlog=_first_state_value(data, 'MAX_POINT_BACKLOG')
        )

    def as_env(self) -> dict[str, str]:
        """
        Return state fields using environment-variable names.

        Returns:
            dict[str, str]: state values keyed by environment variable name.
        """
        result = {}

        if self.interval is not None:
            result['INTERVAL'] = str(self.interval)

        if self.max_point_backlog is not None:
            result['MAX_POINT_BACKLOG'] = str(self.max_point_backlog)

        return result


@define(frozen=True)
class _StateCache:
    """
    Cached UI state snapshot.
    """

    path: Path
    state: UIState
    bucket: int
    expires_at: float


_state_cache: _StateCache | None = None


def _cache_bucket() -> int:
    """
    Return the current wall-clock cache bucket.

    Returns:
        int: cache bucket shared across processes.
    """
    return int(time() // _STATE_CACHE_TTL_SECONDS)


def _shared_cache_path(path: Path) -> Path:
    """
    Return the shared cache file path for a state file.

    Args:
        path (Path): state file path.

    Returns:
        Path: shared cache file path.
    """
    return path.with_name(f'.{path.name}.cache')


def _shared_cache_lock_path(path: Path) -> Path:
    """
    Return the shared cache lock file path for a state file.

    Args:
        path (Path): state file path.

    Returns:
        Path: shared cache lock file path.
    """
    return path.with_name(f'.{path.name}.cache.lock')


@contextmanager
def _shared_cache_lock(path: Path) -> Iterator[None]:
    """
    Lock shared cache refreshes across local processes.

    Args:
        path (Path): state file path.

    Yields:
        None: while the shared cache refresh lock is held.
    """
    import fcntl

    lock_path = _shared_cache_lock_path(path)
    lock_path.parent.mkdir(parents=True, exist_ok=True)

    with lock_path.open('a', encoding='utf-8') as lock_file:
        fcntl.flock(lock_file, fcntl.LOCK_EX)

        try:
            yield
        finally:
            fcntl.flock(lock_file, fcntl.LOCK_UN)


def _cache_state(path: Path, state: UIState, bucket: int) -> None:
    """
    Cache a state snapshot for the configured cache interval.

    Args:
        path (Path): state file path.
        state (UIState): state snapshot to cache.
        bucket (int): wall-clock cache bucket.
    """
    global _state_cache

    with _state_cache_lock:
        _state_cache = _StateCache(
            path=path,
            state=state,
            bucket=bucket,
            expires_at=monotonic() + _STATE_CACHE_TTL_SECONDS
        )


def _cached_state(path: Path, bucket: int) -> UIState | None:
    """
    Return the cached state snapshot when it is still fresh.

    Args:
        path (Path): state file path.
        bucket (int): wall-clock cache bucket.

    Returns:
        UIState | None: cached state, or None when the cache should be refreshed.
    """
    with _state_cache_lock:
        if _state_cache is None:
            return None

        if _state_cache.path != path:
            return None

        if _state_cache.bucket != bucket:
            return None

        if monotonic() >= _state_cache.expires_at:
            return None

        return _state_cache.state


def _read_shared_cache(path: Path, bucket: int) -> UIState | None:
    """
    Read the shared state cache for the current bucket.

    Args:
        path (Path): state file path.
        bucket (int): wall-clock cache bucket.

    Returns:
        UIState | None: shared cache state, or None when stale or missing.
    """
    try:
        with _shared_cache_path(path).open(encoding='utf-8') as cache_file:
            payload = json.load(cache_file)
    except (FileNotFoundError, JSONDecodeError, OSError):
        return None

    if not isinstance(payload, dict):
        return None

    if payload.get('bucket') != bucket:
        return None

    state = payload.get('state')

    if not isinstance(state, dict):
        return None

    return UIState.from_mapping(state)


def _write_shared_cache(path: Path, bucket: int, state: UIState) -> None:
    """
    Atomically write the shared state cache.

    Args:
        path (Path): state file path.
        bucket (int): wall-clock cache bucket.
        state (UIState): state snapshot to cache.
    """
    cache_path = _shared_cache_path(path)
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    fd, tmp_path = tempfile.mkstemp(
        dir=cache_path.parent,
        prefix=f'.{cache_path.name}.',
        text=True
    )

    try:
        with os.fdopen(fd, 'w') as tmp_file:
            json.dump(
                {
                    'bucket': bucket,
                    'state': state.as_env(),
                },
                tmp_file,
                indent=2,
                sort_keys=True
            )
            tmp_file.write('\n')

        Path(tmp_path).replace(cache_path)
    finally:
        try:
            Path(tmp_path).unlink()
        except FileNotFoundError:
            pass


def _try_write_shared_cache(path: Path, bucket: int, state: UIState) -> None:
    """
    Write the shared state cache when the state directory allows it.

    Args:
        path (Path): state file path.
        bucket (int): wall-clock cache bucket.
        state (UIState): state snapshot to cache.
    """
    try:
        _write_shared_cache(path, bucket, state)
    except OSError:
        pass


def _read_state_file(path: Path) -> UIState:
    """
    Read the persisted UI state file without consulting the cache.

    Args:
        path (Path): state file path.

    Returns:
        UIState: persisted UI state, or empty state when the file is missing or invalid.
    """
    try:
        with path.open(encoding='utf-8') as state_file:
            data = json.load(state_file)
    except (FileNotFoundError, JSONDecodeError, OSError):
        return UIState()

    if not isinstance(data, dict):
        return UIState()

    return UIState.from_mapping(data)


def _refresh_state_cache(path: Path, bucket: int) -> UIState:
    """
    Refresh the shared cache from the state file when needed.

    Args:
        path (Path): state file path.
        bucket (int): wall-clock cache bucket.

    Returns:
        UIState: cached state snapshot.
    """
    try:
        with _shared_cache_lock(path):
            state = _read_shared_cache(path, bucket)

            if state is None:
                state = _read_state_file(path)
                _try_write_shared_cache(path, bucket, state)
    except OSError:
        state = _read_state_file(path)

    _cache_state(path, state, bucket)
    return state


def read_state(path: Path | str | None = None) -> UIState:
    """
    Read the persisted UI state file.

    Args:
        path (Path | str | None): optional state file path override.

    Returns:
        UIState: persisted UI state, or empty state when the file is missing or invalid.
    """
    state_path = _state_path(path)
    bucket = _cache_bucket()
    state = _cached_state(state_path, bucket)

    if state is not None:
        return state

    state = _read_shared_cache(state_path, bucket)

    if state is not None:
        _cache_state(state_path, state, bucket)
        return state

    return _refresh_state_cache(state_path, bucket)


def write_state(state: UIState, path: Path | str | None = None) -> None:
    """
    Atomically write the persisted UI state file.

    Args:
        state (UIState): UI state to persist.
        path (Path | str | None): optional state file path override.
    """
    state_path = _state_path(path)
    state_path.parent.mkdir(parents=True, exist_ok=True)

    fd, tmp_path = tempfile.mkstemp(
        dir=state_path.parent,
        prefix=f'.{state_path.name}.',
        text=True
    )

    try:
        with os.fdopen(fd, 'w') as tmp_file:
            json.dump(state.as_env(), tmp_file, indent=2, sort_keys=True)
            tmp_file.write('\n')

        Path(tmp_path).replace(state_path)
        bucket = _cache_bucket()
        _try_write_shared_cache(state_path, bucket, state)
        _cache_state(state_path, state, bucket)
    finally:
        try:
            Path(tmp_path).unlink()
        except FileNotFoundError:
            pass


def update_state(path: Path | str | None = None, **updates: Any) -> UIState:
    """
    Update and persist selected UI state fields.

    Args:
        path (Path | str | None): optional state file path override.
        **updates (Any): state values to update.

    Returns:
        UIState: updated UI state.
    """
    current = read_state(path).as_env()
    current.update({
        key: value
        for key, value in updates.items()
        if key in STATE_FIELD_NAMES
    })

    state = UIState.from_mapping(current)
    write_state(state, path)
    return state


def configured_env_value(name: str, fallback: str) -> str:
    """
    Return a state-backed environment value.

    Args:
        name (str): environment variable name.
        fallback (str): fallback value from the process environment.

    Returns:
        str: state value when present, otherwise the fallback value.
    """
    return read_state().as_env().get(name, fallback)
