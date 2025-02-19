from dataclasses import dataclass


@dataclass
class File:
    file_name: str
    content: str
