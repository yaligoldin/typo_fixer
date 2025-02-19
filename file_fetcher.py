from typing import List, Dict, Optional
import requests
from typo_fixer.file import File


class InvalidRepoName(Exception):
    pass


class APIError(Exception):
    pass


class FileFetcher:
    ID = "id"
    PROJECTS = "projects"
    REPOSITORY = "repository"
    TREE = "tree"
    FILES = "files"
    PATH = "path"
    NAME = "name"
    SUCCESS = 200
    ENCODED_SLASH = "%2F"
    RAW = "raw"
    TWO_LAST_PARTS = -2
    RECURSIVE = "recursive=True"

    def __init__(self, repository_path: str, git_path: str):
        self.repository_path: str = repository_path
        self.git_path: str = git_path

    def _get_file_content(self, project_path: str, file_path: str) -> str:
        file_path_coded = file_path.replace('/', self.ENCODED_SLASH)
        url = f"{self.git_path}/{self.PROJECTS}/{project_path}/{self.REPOSITORY}/{self.FILES}/{file_path_coded}/" \
              f"{self.RAW}"
        response = requests.get(url)
        if response.status_code == self.SUCCESS:
            return response.content.decode()
        raise APIError

    def _get_files_content(self, response: Dict, project_path: str):
        files: List[File] = []
        for file in response:
            file_content = self._get_file_content(project_path, file[self.PATH])
            files.append(File(file[self.NAME], file_content))
        return files

    def fetch_files(self) -> Optional[List[File]]:
        try:
            project_path = self._parse_repository_path()
        except InvalidRepoName:
            print("invalid repo name")
            return
        url = f"{self.git_path}/{self.PROJECTS}/{project_path}/{self.REPOSITORY}/{self.TREE}?{self.RECURSIVE}"
        response = requests.get(url)
        if response.status_code != self.SUCCESS:
            raise APIError(response.status_code)
        files = self._get_files_content(response.json(), project_path)
        return files

    def _parse_repository_path(self):
        parts = self.repository_path.split("/")
        if len(parts) >= 2:
            return self.ENCODED_SLASH.join(parts[self.TWO_LAST_PARTS:])
        raise InvalidRepoName
