"""
get repository from cli
"""
import argparse


def get_repository_from_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("repository", help="enter the repository you want to read here")
    args = parser.parse_args()
    return args.repository
