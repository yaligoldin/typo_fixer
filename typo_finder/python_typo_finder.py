import ast
import io
import re
import string
import tokenize
from typing import List, Tuple, Dict
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

    def __init__(self, file_name: str, file_content: str):
        self.file_name = file_name
        self.file_content = file_content
        self.typos: List[Tuple[str, int]] = []
        self.special_python_function = ["__init__", "__str__", "__repr__", "__call__"]
        self.detectable_code_parts: Dict = {ast.ClassDef: self._check_caml_case_convention,
                                            ast.Assign: self._check_variable_name,
                                            ast.FunctionDef: self._check_functions_names,
                                            ast.arguments: self._check_arguments}

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

    def _attract_comments(self) -> List[Tuple[str, int]]:
        comments: List[Tuple[str, int]] = []
        tokens = tokenize.generate_tokens(io.StringIO(self.file_content).readline)
        last_token = ""
        for token in tokens:
            if self.is_comment(last_token, token):
                comments.append((token.string[1:], token.start[self.LINE]))
            last_token = token.string
        return comments

    def _check_comments_typo(self):
        comments: List[Tuple[str, int]] = self._attract_comments()
        for comment in comments:
            comments_words = comment[self.COMMENT].split(" ")
            self._check_typo_word(comments_words, comment[self.LINE_NUMBER])

    def _check_caml_case_convention(self, statement: ast.ClassDef):
        words_in_class_name = re.findall(r"[A-Z][a-z]*", statement.name)
        self._check_typo_word(words_in_class_name, statement.lineno)

    def _check_arguments(self, statement: ast.arguments):
        arguments = [argument.arg for argument in statement.args]
        if arguments:
            self._check_dander_conversion(arguments, statement.args[0].lineno)

    def _check_functions_names(self, statement: ast.FunctionDef):
        if statement.name in self.special_python_function:
            return
        self._check_dander_conversion([statement.name], statement.lineno)

    def _check_variable_name(self, statement: ast.Assign):
        identifier_options = {ast.Attribute: "attr", ast.Name: "id"}
        arguments_names: List[str] = []
        for target in statement.targets:
            arguments_names.append(getattr(target, identifier_options[type(target)]))
        self._check_dander_conversion(arguments_names, statement.lineno)

    def _check_dander_conversion(self, names_of_code_parts: List[str], line_number: int):
        for code_part in names_of_code_parts:
            words_in_variables_names = code_part.split("_")
            self._check_typo_word(words_in_variables_names, line_number)

    def _check_statement_name(self, statement: ast.AST) -> None:
        for type_of_statement, check_typo in self.detectable_code_parts.items():
            if isinstance(statement, type_of_statement):
                check_typo(statement)
                return

    def _find_typos_in_code_parts(self) -> None:
        syntax_tree = ast.parse(self.file_content)
        for statement in ast.walk(syntax_tree):
            if type(statement) in self.detectable_code_parts:
                self._check_statement_name(statement)


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
        self._find_typos_in_code_parts()
        self._check_comments_typo()
        return FileTypo(self.file_name, self.typos)
