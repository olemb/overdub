import os
import argparse
from .deck import Deck


def parse_args():
    parser = argparse.ArgumentParser()
    arg = parser.add_argument

    arg('--terminal', '-t', action='store_true', help='run in terminal')
    arg('--minimalist', '-m', action='store_true', help='use minimalst UI')
    arg('--gamepad', '-g', action='store_true', help='use gamepad for controls')
    arg('--punch-pedal', '-p', action='store_true', help='punch in/out pedal')
    arg('filename', metavar='file.wav', help='WAV file to overdub onto')

    return parser.parse_args()


def main():
    args = parse_args()
    deck = Deck()

    if args.gamepad:
        from overdub import gamepad_controls
        gamepad_controls.start(deck.do)

    if args.punch_pedal:
        from overdub import punch_pedal
        punch_pedal.start(deck.do)

    if args.terminal:
        from .terminal_ui import ui
    else:
        from .tkinter_ui import ui

    ui(deck, args.filename, minimalist=args.minimalist)
