import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    arg = parser.add_argument

    arg('--terminal', '-t', action='store_true', help='Run in terminal')
    arg('--minimalist', '-m', action='store_true', help='Minimalst UI')
    arg('infile', nargs='?')

    return parser.parse_args()


def main():
    args = parse_args()

    if args.terminal:
        from .terminal_ui import mainloop
    else:
        from .tkinter_ui import mainloop

    mainloop(args)
