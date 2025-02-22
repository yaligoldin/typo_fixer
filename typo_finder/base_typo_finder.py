"""
base file finder
"""
import abc
from abc import ABC
from dataclasses import dataclass
from typing import List

from typo_fixer.file import File


@dataclass
class Typo:
    typo: str
    typo_line: int

    def __str__(self):
        return f"typo: {self.typo} typo_line: {self.typo_line}\n"


@dataclass
class FileTypo:
    file: File
    typos: List[Typo]

    def __str__(self):
        file_typo_description = f"there were typos in: {self.file.file_name}:\n"
        for typo in self.typos:
            file_typo_description += str(typo)
        return file_typo_description


class BaseTypoFinder(ABC):
    @abc.abstractmethod
    def find_typos(self) -> FileTypo:
        raise NotImplementedError
