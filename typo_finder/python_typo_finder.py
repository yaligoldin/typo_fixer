"""
python file typo finder
"""
import io
import re
import string
import tokenize
from typing import List, Tuple, Set
from spellchecker import SpellChecker
from typo_fixer.typo_finder.base_typo_finder import BaseTypoFinder, FileTypo


class PythonTypoFinder(BaseTypoFinder):
    LINE = 0
    LINE_NUMBER = 1
    COMMENT = 0
    QUOTATION = "'"
    APOSTROPHE = '"'
    DOCSTRING_LEN = 3
    EQUAL = "="
    CONTENT = 0
    COMMENT_SIGN = 1

    def __init__(self, file_name: str, file_content: str):
        self.file_name = file_name
        self.file_content = file_content
        self.typos: List[Tuple[str, int]] = []
        self.special_python_function = ["__init__", "__str__", "__repr__", "__call__", "def"]
        self.split_ways = [self._split_dander, self._split_caml_case]

    @staticmethod
    def _split_dander(statement_to_split: str) -> List[str]:
        return statement_to_split.split("_")

    @staticmethod
    def _split_caml_case(statement_to_split: str) -> List[str]:
        return re.findall(r"[A-Z][a-z]*", statement_to_split)

    def is_docstring(self, last_token: str, token: tokenize.TokenInfo, quotation_sign: str) -> bool:
        return token.string[:self.DOCSTRING_LEN] == f"{quotation_sign}{quotation_sign}{quotation_sign}" \
               and token.string[-self.DOCSTRING_LEN:] == f"{quotation_sign}{quotation_sign}{quotation_sign}" \
               and last_token != self.EQUAL

    def is_comment(self, last_token: str, token: tokenize.TokenInfo) -> bool:
        if token.type == tokenize.COMMENT:
            return True
        return self.is_docstring(last_token, token, self.QUOTATION) or self.is_docstring(last_token, token,
                                                                                         self.APOSTROPHE)

    def _scan_content(self) -> Set[Tuple[str, int]]:
        tokens = tokenize.generate_tokens(io.StringIO(self.file_content).readline)
        last_token = ""
        statements: Set[Tuple[str, int]] = set()
        for token in tokens:
            if self.is_comment(last_token, token):
                statements.add((token.string[self.COMMENT_SIGN:], token.start[self.LINE]))
            last_token = token.string
            if token.type == tokenize.NAME:
                statements.add((token.string, token.start[self.LINE]))
        return statements

    def _check_statement_typo(self, statements: Set[Tuple[str, int]]) -> None:
        for statement in statements:
            self._check_statement(statement[self.CONTENT], statement[self.LINE_NUMBER])

    def _split_statement_to_words(self, statement_to_split: str) -> List[str]:
        for split_way in self.split_ways:
            statement_words = split_way(statement_to_split)
            if len(statement_words) > 1:
                return statement_words
        return statement_to_split.split(" ")

    def _check_statement(self, statement_to_check: str, line_number: int) -> None:
        if statement_to_check in self.special_python_function:
            return
        statements_words = self._split_statement_to_words(statement_to_check)
        self._check_typo_word(statements_words, line_number)

    def _remove_empty_strings(self, words: List[str]) -> List[str]:
        not_empty_words: List[str] = []
        white_spaces = [self.QUOTATION, self.APOSTROPHE]
        white_spaces.extend(string.whitespace)
        for word in words:
            for white_char in white_spaces:
                word = word.replace(white_char, "")
            if word:
                not_empty_words.append(word)
        return not_empty_words

    def _check_typo_word(self, words: List[str], line_number: int) -> None:
        spell_checker = SpellChecker()
        spell_checker.word_frequency.load_words(dir(__builtins__))
        words = self._remove_empty_strings(words)
        for word in words:
            if word.lower() not in spell_checker:
                self.typos.append((word, line_number))

    def find_typos(self) -> FileTypo:
        statements = self._scan_content()
        self._check_statement_typo(statements)
        return FileTypo(self.file_name, self.typos)
