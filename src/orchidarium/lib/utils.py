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
    if 'Sensor' not in sys.modules:
        from orchidarium.sensors import Sensor

    subclasses = []
    for _, obj in inspect.getmembers(orchidarium.sensors, inspect.isclass):
        if issubclass(obj, Sensor) and obj is not Sensor:
            subclasses.append(obj)
    return len(subclasses)