"""
base file finder
"""
import abc
from abc import ABC
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class FileTypo:
    file_name: str
    typos: List[Tuple[str, int]]

    def __str__(self):
        return f"there were typos in: {self.file_name} in those lines: {self.typos}"


class BaseTypoFinder(ABC):
    @abc.abstractmethod
    def find_typos(self) -> FileTypo:
        raise NotImplementedError
