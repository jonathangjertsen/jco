import sys

import jco
from jco.exceptions import JcoTerminate
from jco.options import Option


class Command(object):
    commands = {}

    def __init__(self, func):
        self.func = func
        Command.commands[func.__name__] = self

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


@Command
def help(*args):
    """Help."""
    print("Available commands:")
    for command in Command.commands:
        print("\t{}: {}".format(command, Command.commands[command].__doc__))
    print()
    print("Available options (space-separated list of <option>=<value>):")
    print(Option.opt_info())


@Command
def one(args):
    """Info about one number: jco one <number>"""
    print(jco.one(*args))


@Command
def two(args):
    """Info about 2 numbers: jco two <a> <b>"""
    print(jco.two(*args))


@Command
def n(args):
    if len(args) == 1:
        one(args)
    elif len(args) == 2:
        two(args)
    else:
        raise JcoTerminate(f"n does not support {len(args)} args")


def main():
    cli_args = sys.argv[1:]

    if not cli_args:
        help()
        return

    command = cli_args[0]
    command_args = []

    for i in range(1, len(cli_args)):
        if "=" in cli_args[i]:
            key, value = cli_args[i].split("=")
            jco.Option.set(key, value)
        else:
            command_args.append(cli_args[i])

    if command in Command.commands:
        Command.commands[command](command_args)
    else:
        try:
            n_args = [command] + command_args
            n(n_args)
        except Exception as exc:
            print(f"Tried running 'jco n {' '.join(n_args)}', got error: {exc}")
            print(f"Available commands: {list(Command.commands)}")


def entry():
    try:
        main()
    except JcoTerminate as jt:
        print(jt)


if __name__ == "__main__":
    entry()
