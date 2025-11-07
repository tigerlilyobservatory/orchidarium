"""
Random helpful utility functions.
"""


import sys

from functools import lru_cache


@lru_cache(maxsize=1)
def sensor_count() -> int:
    """
    Return the number of supported sensors.

    Returns:
        int: the number of supported sensors [0-inf).
    """
    import inspect

    if 'orchidarium.sensors' not in sys.modules:
        import orchidarium.sensors

    subclasses = []
    for _, obj in inspect.getmembers(orchidarium.sensors, inspect.isclass):
        if issubclass(obj, orchidarium.sensors.Sensor) and obj is not orchidarium.sensors.Sensor:
            subclasses.append(obj)
    return len(subclasses)