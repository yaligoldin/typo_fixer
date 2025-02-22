"""
file factory and ending enum
"""
from typing import Dict, Callable, Optional, List
from enum import Enum

from typo_fixer.file import File
from typo_fixer.typo_finder.base_typo_finder import BaseTypoFinder
from typo_fixer.typo_finder.python_typo_finder import PythonTypoFinder
from typo_fixer.typo_finder.txt_typo_finder import TxtTypoFinder


class FileType(Enum):
    PY = "py"
    TXT = "txt"


FILES_TYPES = [FileType.PY.value, FileType.TXT.value]


class InValidFileNameError(Exception):
    pass


class FileFactory:
    LAST = -1

    def __init__(self):
        self.file_factory: Dict[str, Callable[[File], BaseTypoFinder]] = {FileType.PY.value: PythonTypoFinder,
                                                                          FileType.TXT.value: TxtTypoFinder}

    def _validate_file_type(self, file_parts: List[str]) -> str:
        try:
            file_type = file_parts[self.LAST]
        except IndexError:
            raise InValidFileNameError
        if file_type not in FILES_TYPES:
            raise InValidFileNameError
        return file_type

    def _get_file_type(self, file_name: str) -> str:
        file_parts = file_name.split(".")
        return self._validate_file_type(file_parts)

    def create_file_finder(self, file: File) -> Optional[BaseTypoFinder]:
        try:
            file_type = self._get_file_type(file.file_path)
        except InValidFileNameError:
            return None
        return self.file_factory[file_type](file)
