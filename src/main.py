import argparse

from stest import stest
from stest import utils

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", help="Command to execute", choices=["init", "add", "create-tests"])
    args = parser.parse_args()

    app = stest.Stest()

    if args.command == "init":
        app.init(utils.relative_path_to_absolute_path("./"))

if __name__ == "__main__":
    main()
