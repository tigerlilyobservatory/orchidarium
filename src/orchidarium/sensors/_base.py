from __future__ import annotations

from abc import abstractmethod, ABC
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from orchidarium.publishers._base import Publisher
    from typing import Literal


class Sensor(ABC):

    def __init__(self, scale: Literal['F', 'C'] = 'F') -> None:
        self.scale = scale

    @property
    def temperature(self) -> float:
        return self._temperature

    @temperature.setter
    def _(self, value: float) -> None:
        self._temperature = value

    @temperature.getter
    def _(self) -> float:
        if self.scale == 'F':
            return self._temperature * 9 / 5 + 32.0
        elif self.scale == 'C':
            return self._temperature
        else:
            return self._temperature

    @abstractmethod
    def collect(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def publish(self, publisher: Publisher) -> bool:
        raise NotImplementedError