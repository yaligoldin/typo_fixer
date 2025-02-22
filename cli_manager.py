"""
get repository from cli
"""
import argparse


def get_arguments_from_cli() -> str:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository", help="enter the repository you want to read here")
    parser.add_argument("local_path", help="enter the local path that the fixed files will be copy to")
    args = parser.parse_args()
    return args.repository, args.local_path
