import argparse

from stest import stest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", help="Command to execute", choices=["init", "add", "create-tests"])
    args = parser.parse_args()

    app = stest.Stest()

    if args.command == "init":
        app.init(".")

if __name__ == "__main__":
    main()
