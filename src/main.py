import argparse
from stest import stest
import os
from colorama import Fore, Style

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")

    # Subparser for init
    init_parser = subparsers.add_parser("init", help="Initialize something")
    init_parser.add_argument("projectDir", nargs="?", default=os.getcwd(), help="Project directory") #Accepts 0 or 1 arguments
    init_parser.add_argument("-l", "--language", nargs="?", choices=["cpp", "js", "py", "c"], help="Programming language of the files")
    init_parser.add_argument("-o", "--output", nargs="?", default="./tests", help="Output directory")

    # Subparser for add
    add_parser = subparsers.add_parser("add", help="Add files")
    add_parser.add_argument("files", nargs="+", help="Files to add")

    # Subparser for remove
    remove_parser = subparsers.add_parser("remove", help="Remove files")
    remove_parser.add_argument("files", nargs="+", help="Files to remove")

    # Subparser for status
    subparsers.add_parser("status", help="Show status")

    # Subparser for create-tests
    subparsers.add_parser("create-tests", help="Create tests")

    args = parser.parse_args()

    app = stest.Stest()

    try:
        if args.command == "init":
            app.init(args.projectDir, args.output, args.language)
        elif args.command == "add":
            app.add(args.files)
        elif args.command == "remove":
            app.remove(args.files)
        elif args.command == "create-tests":
            app.create_tests()
        elif args.command == "status":
            app.status()
    except Exception as e:
        print(f"{Fore.RED}Error: {Style.RESET_ALL}{e}")


if __name__ == "__main__":
    main()
