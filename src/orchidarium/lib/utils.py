"""
Random helpful utility functions.
"""


from functools import lru_cache


@lru_cache(maxsize=1)
def sensor_count() -> int:
    """
    Return the number of supported sensors.

    Returns:
        int: the number of supported sensors [0-inf).
    """
    import inspect
    import orchidarium.sensors

    from orchidarium.sensors import Sensor

    subclasses = []
    for _, obj in inspect.getmembers(orchidarium.sensors, inspect.isclass):
        if issubclass(obj, Sensor) and obj is not Sensor:
            subclasses.append(obj)
    return len(subclasses)