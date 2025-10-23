from __future__ import annotations

from abc import abstractmethod, ABC
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from orchidarium.publishers._base import Publisher


class Sensor(ABC):

    @abstractmethod
    def collect(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def publish(self, publisher: Publisher) -> bool:
        raise NotImplementedError