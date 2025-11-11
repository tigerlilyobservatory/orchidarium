import orchidarium.sensors

from functools import lru_cache
# from cachetools import TTLCache
# from orchidarium import env


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