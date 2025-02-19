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

    def __init__(self, file_name: str, file_content: str):
        self.file_name = file_name
        self.file_content = file_content
        self.typos: List[Tuple[str, int]] = []
        self.special_python_function = ["__init__", "__str__", "__repr__", "__call__", "def"]

    def is_docstring(self, last_token: str, token: tokenize.TokenInfo) -> bool:
        if token.string[:self.DOCSTRING_LEN] == f"{self.QUOTATION}{self.QUOTATION}{self.QUOTATION}" \
                and token.string[-self.DOCSTRING_LEN:] == f"{self.QUOTATION}{self.QUOTATION}{self.QUOTATION}" \
                and last_token != self.EQUAL:
            return True
        return token.string[:self.DOCSTRING_LEN] == f"{self.APOSTROPHE}{self.APOSTROPHE}{self.APOSTROPHE}" \
            and token.string[-self.DOCSTRING_LEN:] == f"{self.APOSTROPHE}{self.APOSTROPHE}{self.APOSTROPHE}" \
            and last_token != self.EQUAL

    def is_comment(self, last_token: str, token: tokenize.TokenInfo) -> bool:
        if token.type == tokenize.COMMENT:
            return True
        return self.is_docstring(last_token, token)

    def _scan_content(self) -> Tuple[List[Tuple[str, int]], Set[Tuple[str, int]]]:
        comments: List[Tuple[str, int]] = []
        tokens = tokenize.generate_tokens(io.StringIO(self.file_content).readline)
        last_token = ""
        names: Set[Tuple[str, int]] = set()
        for token in tokens:
            if self.is_comment(last_token, token):
                comments.append((token.string[1:], token.start[self.LINE]))
            last_token = token.string
            if token.type == tokenize.NAME:
                names.add((token.string, token.start[self.LINE]))
        return comments, names

    def _check_comments_typo(self, comments: List[Tuple[str, int]]):
        for comment in comments:
            comments_words = comment[self.COMMENT].split(" ")
            self._check_typo_word(comments_words, comment[self.LINE_NUMBER])

    def _check_statement_typo(self, code_statements: Set[Tuple[str, int]]):
        for statement in code_statements:
            self._check_statement(statement[self.CONTENT], statement[self.LINE_NUMBER])

    @staticmethod
    def _split_statement_to_words(statement_to_check: str):
        statement_words = statement_to_check.split("_")
        if len(statement_words) > 1:
            return statement_words
        statement_words = re.findall(r"[A-Z][a-z]*", statement_to_check)
        if len(statement_words) > 1:
            return statement_words
        return [statement_to_check]

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

    def _check_typo_word(self, words: List[str], line_number: int):
        spell_checker = SpellChecker()
        spell_checker.word_frequency.load_words(dir(__builtins__))
        words = self._remove_empty_strings(words)
        for word in words:
            if word.lower() not in spell_checker:
                self.typos.append((word, line_number))

    def find_typos(self) -> FileTypo:
        comments, names = self._scan_content()
        self._check_comments_typo(comments)
        self._check_statement_typo(names)
        return FileTypo(self.file_name, self.typos)
