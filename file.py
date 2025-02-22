"""
file dataclass
"""
from dataclasses import dataclass


@dataclass
class File:
    file_path: str
    content: str
