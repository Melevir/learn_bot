import argparse


def compose_command_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--command", action="store", default=None, help="Command to run")
    return parser
