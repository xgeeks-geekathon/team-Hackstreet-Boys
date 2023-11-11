import argparse
from stest import stest
import os

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")

    # Subparser for init
    init_parser = subparsers.add_parser("init", help="Initialize something")
    init_parser.add_argument("projectDir", nargs="?", default=os.getcwd(), help="Project directory") #Accepts 0 or 1 arguments

    # Subparser for add
    add_parser = subparsers.add_parser("add", help="Add files")
    add_parser.add_argument("files", nargs="+", help="Files to add")
    add_parser.add_argument("-l", "--language", nargs="*", help="Language of the files")

    # Subparser for create-tests
    subparsers.add_parser("create-tests", help="Create tests")

    args = parser.parse_args()

    app = stest.Stest()

    if args.command == "init":
            app.init(args.projectDir)
    elif args.command == "add":
        app.add(*args.files)
    elif args.command == "create-tests":
        app.create_tests()

if __name__ == "__main__":
    main()
