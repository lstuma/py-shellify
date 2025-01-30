from argparse import ArgumentParser
from .core import Client

parser = ArgumentParser(prog="pyshell", description="Improved shell scripting using Python!")

def run():
    parser.add_argument("code", type=str, help="The python code to run")
    args = parser.parse_args()
    Client.execute_code(args.code)

def close():
    pass

def close_all():
    pass

def create_handler():
    """
    Runs the handler in the background as a child process.
    """
    pass

def main():
    # default behaviour -> run
    run()

if __name__ == "__main__":
    main()
