import abc
from typing import Any


class BaseRepository(abc.ABC):
    def __init__(self, reference_type):
        self._reference_type = reference_type

    @abc.abstractmethod
    def add(self, obj: Any) -> None:
        ...

    @abc.abstractmethod
    def get(self, reference: int) -> Any:
        ...

    @abc.abstractmethod
    def update(self, obj: Any) -> None:
        ...

    @abc.abstractmethod
    def remove(self, reference: int) -> None:
        ...

    @abc.abstractmethod
    def list(self) -> list[Any]:
        ...
