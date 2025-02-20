"""
txt typo finder
"""
from typing import Tuple, List
from spellchecker import SpellChecker
from file import File
from base_typo_finder import BaseTypoFinder, FileTypo


class TxtTypoFinder(BaseTypoFinder):

    def __init__(self, file: File):
        self.file: File = file

    @staticmethod
    def _attract_typos_in_content(spell_checker: SpellChecker, content_lines: List[str]) -> List[Tuple[str, int]]:
        typos: List[Tuple[str, int]] = []
        for line_number, line in enumerate(content_lines):
            words_in_line: List[str] = line.split(" ")
            for word in words_in_line:
                if word not in spell_checker:
                    typos.append((word, line_number))
        return typos

    def find_typos(self) -> FileTypo:
        spell_checker = SpellChecker()
        content_lines = self.file.content.splitlines()
        typos: List[Tuple[str, int]] = (self._attract_typos_in_content(spell_checker, content_lines))
        return FileTypo(self.file.file_name, typos)
