import os
import argparse
from overdub.deck import audio
from overdub.deck import Deck


def parse_args():
    parser = argparse.ArgumentParser()
    arg = parser.add_argument

    arg('--terminal', '-t', action='store_true', help='run in terminal')
    arg('--minimalist', '-m', action='store_true', help='use minimalst UI')
    arg('filename', metavar='file.wav', help='WAV file to overdub onto')

    return parser.parse_args()


def main():
    args = parse_args()
    deck = Deck()

    if args.terminal:
        from .terminal_ui import mainloop
    else:
        from .tkinter_ui import mainloop

    mainloop(deck, args)
