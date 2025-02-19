"""
main
"""
from typo_fixer.cli_manager import get_repository_from_cli
from typo_fixer.file_factory import FileFactory
from typo_fixer.file_fetcher import FileFetcher, APIError

GIT_PATH = "https://gitlab.com/api/v4"


def main():
    repository = get_repository_from_cli()
    try:
        files = FileFetcher(repository, GIT_PATH).fetch_files()
    except APIError:
        print("there were a problem with the API")
        return
    file_factory = FileFactory()
    files_typo_finders = [file_factory.create_file_finder(file) for file in files if
                          file_factory.create_file_finder(file)]
    for file_typo_finder in files_typo_finders:
        print(file_typo_finder.find_typos())


if __name__ == '__main__':
    main()
