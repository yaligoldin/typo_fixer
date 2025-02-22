"""
main
"""
from typo_fixer.cli_manager import get_arguments_from_cli
from typo_fixer.file_factory import FileFactory
from typo_fixer.file_fetcher import FileFetcher, APIError
from typo_fixer.fixer_typo import TypoFixer

GIT_PATH = "https://gitlab.com/api/v4"


def main():
    repository, fixed_files_local_path = get_arguments_from_cli()
    try:
        files = FileFetcher(repository, GIT_PATH).fetch_files()
    except APIError:
        print("there were a problem with the API")
        return
    file_factory = FileFactory()
    files_typo_finders = [file_factory.create_file_finder(file) for file in files if
                          file_factory.create_file_finder(file)]
    typo_fixer = TypoFixer(fixed_files_local_path)
    for typo_finder in files_typo_finders:
        typo_fixer.create_fixed_file(typo_finder.find_typos())


if __name__ == '__main__':
    main()
