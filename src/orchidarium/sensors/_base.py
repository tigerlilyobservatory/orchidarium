from __future__ import annotations

from pathlib import Path
from abc import abstractmethod, ABC
from orchidarium.lib.json import write_json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from orchidarium.publishers._base import Publisher
    from typing import Literal


class Sensor(ABC):

    def __init__(self, scale: Literal['F', 'C'] = 'F') -> None:
        self.scale = scale
        self._collection: bool = False
        self._publication: bool = False

    @property
    def temperature(self) -> float:
        if self.scale == 'F':
            return self._temperature * 9 / 5 + 32.0
        elif self.scale == 'C':
            return self._temperature
        else:
            return self._temperature

    @temperature.setter
    def temperature(self, value: float) -> None:
        self._temperature = value

    @abstractmethod
    def collect(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def publish(self, publisher: Publisher) -> bool:
        raise NotImplementedError

    def cache(self, file: Path = Path('healthcheck.json')) -> bool:
        """
        Write a cache to disk that healthchecks can pick up on to indicate the proper health.

        Args:
            file (Path): File to cache healthcheck results in. (default: Path('healthcheck.json'))

        Returns:
            bool: True if caching the result was successful; False otherwise.
        """
        return write_json(
            data={
                "healthcheck": {
                    "publish": self._publication,
                    "readout": self._collection
                }
            },
            path=Path(self.__class__.__name__.lower() + '_' + str(file))
        )