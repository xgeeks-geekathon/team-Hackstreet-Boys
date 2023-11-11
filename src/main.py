import argparse
import asyncio
from stest import stest
import os


async def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")

    # Subparser for init
    init_parser = subparsers.add_parser("init", help="Initialize something")
    init_parser.add_argument("projectDir", nargs="?", default=os.getcwd(),help="Project directory")
    init_parser.add_argument("-o", "--outputDir", nargs="?", default= os.path.join(os.getcwd(), 'tests'), help="Tests destination folder")
    init_parser.add_argument("-l", "--language", nargs="?", choices=["cpp", "js", "py", "c"], help="Programming language of the files")

    # Subparser for add
    add_parser = subparsers.add_parser("add", help="Add files")
    add_parser.add_argument("files", nargs="+", help="Files to add")
    

    # Subparser for remove
    remove_parser = subparsers.add_parser("remove", help="Remove files")
    remove_parser.add_argument("files", nargs="+", help="Files to remove")

    # Subparser for create-tests
    subparsers.add_parser("create-tests", help="Create tests")

    args = parser.parse_args()

    app = stest.Stest()

    try:
        if args.command == "init":
            app.init(args.projectDir, args.outputDir, args.language)
        elif args.command == "add":
            await app.add(args.files)
        elif args.command == "remove":
            app.remove(args.files)
        elif args.command == "create-tests":
            app.create_tests()
    except Exception as e:
        print(e)


if __name__ == "__main__":
    asyncio.run(main())
