from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
from spellchecker import SpellChecker
from typo_fixer.file import File
from typo_fixer.typo_finder.base_typo_finder import Typo, FileTypo


@dataclass
class FixedTypo:
    typo_word: str
    typo_line: int
    typo_correction: str


class TypoFixer:
    DOCSTRING_START_LEN = 3
    MINIMUM_DOCSTRING_LEN = 6
    TWICE = 2

    def __init__(self, local_fixed_repository: str):
        self.local_fixed_repository: Path = Path(local_fixed_repository)

    def _is_docstring(self, code_line: str) -> bool:
        code_line = code_line.strip()
        return code_line[:self.DOCSTRING_START_LEN] == "'''" or code_line[:self.DOCSTRING_START_LEN] == '"""'

    def check_one_line_docstring(self, first_line) -> Optional[str]:
        if first_line.count(first_line[:self.DOCSTRING_START_LEN]) == self.TWICE and len(
                first_line) >= self.MINIMUM_DOCSTRING_LEN:
            return first_line

    def get_multiple_line_docstring(self, first_line: str, content_lines: List[str], start_line: int) -> str:
        docstring = first_line
        start_docstring = first_line.strip()[:self.DOCSTRING_START_LEN]
        for i in range(start_line + 1, len(content_lines)):
            docstring += f"{content_lines[i]}\n"
            if content_lines[i].strip().endswith(start_docstring):
                content_lines[i] = ""
                break
            content_lines[i] = ""
        return docstring

    def _get_docstring(self, content_lines: List[str], start_line: int) -> str:
        first_line = content_lines[start_line]
        if one_line_docstring := self.check_one_line_docstring(first_line.strip()):
            return one_line_docstring
        return self.get_multiple_line_docstring(first_line, content_lines, start_line)

    def _fix_line(self, content_lines: List[str], typo_to_correct: FixedTypo) -> List[str]:
        line_to_correct = content_lines[typo_to_correct.typo_line - 1]
        if self._is_docstring(line_to_correct):
            line_to_correct = self._get_docstring(content_lines, typo_to_correct.typo_line - 1)
        line_to_correct = line_to_correct.replace(typo_to_correct.typo_word, typo_to_correct.typo_correction)
        content_lines[typo_to_correct.typo_line - 1] = line_to_correct
        return content_lines

    def fix_file(self, file_to_fix: File, typos_corrections: List[FixedTypo]) -> File:
        content_lines = file_to_fix.content.splitlines()
        for typo_to_correct in typos_corrections:
            content_lines = self._fix_line(content_lines, typo_to_correct)
        file_content = "\n".join(content_lines)
        return File(file_to_fix.file_path, file_content)

    @staticmethod
    def _choose_correction_typo(typo_correction_suggestions: Optional[List[str]], typo: Typo) -> str:
        print(f"typo: {typo.typo} in line: {typo.typo_line}")
        if typo_correction_suggestions:
            for typo_correction in typo_correction_suggestions:
                print(typo_correction)
        typo_correction = input("choose correction (if possible) or write one of your own")
        return typo_correction

    def _find_fixed_typo(self, typo: Typo) -> FixedTypo:
        spell_checker = SpellChecker()
        typo_corrections_suggestions = spell_checker.candidates(typo.typo)
        typo_correction = self._choose_correction_typo(typo_corrections_suggestions, typo)
        return FixedTypo(typo.typo, typo.typo_line, typo_correction)

    def create_fixed_file(self, typos: FileTypo) -> None:
        fixed_typos: List[FixedTypo] = []
        print(f"in file file: {typos.file.file_path}")
        for typo in typos.typos:
            fixed_typo = self._find_fixed_typo(typo)
            fixed_typos.append(fixed_typo)
        fixed_file = self.fix_file(typos.file, fixed_typos)
        self._write_fixed_file(fixed_file)

    def _write_fixed_file(self, fixed_file: File) -> None:
        local_fixed_file = Path(self.local_fixed_repository, fixed_file.file_path)
        local_fixed_file.parent.mkdir(parents=True, exist_ok=True)
        local_fixed_file.touch()
        local_fixed_file.write_text(fixed_file.content)
