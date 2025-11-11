from __future__ import annotations

import inspect
import orchidarium.sensors

from functools import lru_cache
# from cachetools import TTLCache
# from orchidarium import env
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Generator, Type
    from orchidarium.sensors import Sensor


@lru_cache(maxsize=1)
def sensor_count() -> int:
    """
    Return the number of supported sensors.

    Returns:
        int: the number of supported sensors [0-inf).
    """
    import inspect

    subclasses = []
    for _, obj in inspect.getmembers(orchidarium.sensors, inspect.isclass):
        if issubclass(obj, orchidarium.sensors.Sensor) and obj is not orchidarium.sensors.Sensor:
            subclasses.append(obj)
    return len(subclasses)


# cache: TTLCache = TTLCache(
#     maxsize=sensor_count(),
#     ttl=int(env['HEALTHCHECK_CACHE_TTL'])
# )


def sensor_generator() -> Generator[Type[Sensor]]:
    """
    Iterate over sensor types with this generator.

    Yields:
        Generator[Type[Sensor]]: A list of current Sensor implementation callables.
    """
    for _, obj in inspect.getmembers(orchidarium.sensors, inspect.isclass):
        if issubclass(obj, orchidarium.sensors.Sensor) and obj is not orchidarium.sensors.Sensor:
            yield obj