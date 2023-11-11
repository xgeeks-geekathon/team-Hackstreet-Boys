import argparse
from stest import stest
from stest import utils
import os

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")

    # Subparser for init
    init_parser = subparsers.add_parser("init", help="Initialize something")
    init_parser.add_argument("projectDir", nargs="?", default=os.getcwd(), help="Project directory") #Accepts 0 or 1 arguments
    init_parser.add_argument("-l", "--language", nargs=1, help="The programming language", required=True)

    # Subparser for add
    add_parser = subparsers.add_parser("add", help="Add files")
    add_parser.add_argument("files", nargs="+", help="Files to add")

    # Subparser for create-tests
    subparsers.add_parser("create-tests", help="Create tests")

    args = parser.parse_args()

    app = stest.Stest()

    try:
        if args.command == "init":
            app.init(args.projectDir, args.language[0])
        elif args.command == "add":
            app.add(args.files)
        elif args.command == "create-tests":
            app.create_tests()
    except Exception as e:
        print(e)
        # Print stack trace
        raise e


if __name__ == "__main__":
    main()
