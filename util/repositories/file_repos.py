import abc
from abc import ABC
from dataclasses import asdict
from typing import Any, List
import json

from util.repositories.base_repo import BaseRepository


class FileRepo(BaseRepository, abc.ABC):
    def __init__(self, reference_type, filename):
        super().__init__(reference_type)

        self._file_repo = []
        self._filename = filename

    def add(self, obj: Any) -> None:
        self._file_repo.append(obj)

    def update(self, obj: Any) -> None:
        raise NotImplemented

    def remove(self, reference: int) -> None:
        del self._file_repo[reference]

    def get(self, reference: int) -> Any:
        return self._file_repo[reference]

    def list(self) -> List[Any]:
        return self._file_repo

    @abc.abstractmethod
    def load_repo(self):
        ...

    @abc.abstractmethod
    def save_repo(self):
        ...

    def __enter__(self):
        self.load_repo()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.save_repo()


class JsonRepo(FileRepo, ABC):
    INDENT_VALUE = 4

    def load_repo(self):
        with open(self._filename, mode="r") as file:
            self._file_repo = json.load(file)

    def save_repo(self):
        with open(self._filename, "w") as file:
            json.dump(self._file_repo, file, indent=self.INDENT_VALUE)


class DataclassJsonRepo(JsonRepo):
    def load_repo(self):
        super().load_repo()
        self._file_repo = [self._reference_type(**item) for item in self._file_repo]

    def save_repo(self):
        self._file_repo = [asdict(item) for item in self._file_repo]
        super().save_repo()
