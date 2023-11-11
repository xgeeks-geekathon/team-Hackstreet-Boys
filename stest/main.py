import stest
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("name", help="name of the user")
    args = parser.parse_args()
    print("Hello, {}".format(args.name))


if __name__ == "__main__":
    main()
