"""
ABC that defines the API for publishing metrics.
"""


from __future__ import annotations

from abc import abstractmethod, ABC
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, List


class Publisher(ABC):

    @abstractmethod
    def connect(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def publish_datapoint(self, datum: Any) -> bool:
        raise NotImplementedError