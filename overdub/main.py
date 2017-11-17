import argparse
from overdub.deck import audio
from overdub.deck import Deck


def parse_args():
    parser = argparse.ArgumentParser()
    arg = parser.add_argument

    arg('--terminal', '-t', action='store_true', help='run in terminal')
    arg('--minimalist', '-m', action='store_true', help='use minimalst UI')
    arg('--backing-track', '-b', dest='backing_track', default=None,
        help='WAV file to play along with recording')
    arg('infile', nargs='?')

    return parser.parse_args()


def main():
    args = parse_args()
    deck = Deck()

    if args.infile is not None:
        deck.blocks = audio.load(args.infile)
    
    if args.backing_track is not None:
        deck.backing_track = audio.load(args.backing_track)

    if args.terminal:
        from .terminal_ui import mainloop
    else:
        from .tkinter_ui import mainloop

    mainloop(args, deck)
