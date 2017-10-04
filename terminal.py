#!/usr/bin/env python3
import os
import sys
import time
import fcntl
import termios
from contextlib import contextmanager
from overdub import audio
from overdub.deck import Deck
from overdub.filenames import make_output_filename


def hide_cursor():
    print('\033[?25l', end='', flush=True)


def show_cursor():
    print('\033[?25h', end='', flush=True)


@contextmanager
def term():
    fd = sys.stdin.fileno()
    oldterm = termios.tcgetattr(fd)
    newattr = termios.tcgetattr(fd)
    newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
    termios.tcsetattr(fd, termios.TCSANOW, newattr)

    oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

    hide_cursor()

    try:
        yield
    finally:
        show_cursor()
        termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
        fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)


def get_event():
    char = sys.stdin.read(1)

    if char == '\x1b':
        code = sys.stdin.read(2)
        if code == '[C':
            return 'wind'
        elif code == '[D':
            return 'rewind'
    elif char == '\x7f':
        return 'undo'
    elif char == 'q':
        return 'quit'
    elif char == 's':
        return 'snapshot'
    elif char == '\n':
        return 'toggle_record'
    elif char == ' ':
        return 'toggle_play'

    return None


def get_events():
    while True:
        event = get_event()
        if event:
            yield event
        else:
            break


def update_line(text):
    maxline = 78
    line = '\r' + text.ljust(maxline)[:78]
    print(line, end='', flush=True)


def color_text(text, color):
    colors = {
        'green':  '92',
        'yellow': '93',
        'red':    '31',
    }
    return '\001\033[' + colors[color] + 'm\002' + text + '\001\033[0m\002'


def make_status_line(deck):
    # This produces some broken characters around the colored text.
    # if deck.mode == 'recording':
    #     mode = color_text('recording', 'red')
    # elif deck.mode == 'playing':
    #     mode = color_text('playing', 'green')
    # else:
    #     mode = deck.mode
    mode = deck.mode

    if deck.can_undo:
        changed = '*'
    else:
        changed = ' '

    if deck.time < 0.1:
        dot = '.'
    else:
        dot = ' '

    # https://en.wikipedia.org/wiki/Media_controls
    if mode == 'recording':
        mode = 'O'
    elif mode == 'playing':
        mode = '>'
    elif mode == 'stopped':
        mode = ' '

    return ' {} {} {}'.format(changed, dot, mode)


def main():
    deck = Deck()

    if sys.argv[1:]:
        deck.blocks = audio.load(sys.argv[1])

    try:
        with term():
            while True:
                for event in get_events():
                    if event == 'quit':
                        return
                    elif event == 'snapshot':
                        filename = make_output_filename(prefix='snapshot')
                        update_line('Saving {}'.format(filename))
                        print()
                        audio.save(filename, deck.blocks)
                    elif event == 'toggle_play':
                        deck.toggle_play()
                    elif event == 'toggle_record':
                        deck.toggle_record()
                    elif event == 'wind':
                        deck.skip(1)
                    elif event == 'rewind':
                        deck.skip(-1)
                    elif event == 'undo':
                        deck.undo()

                update_line(make_status_line(deck))

                time.sleep(0.05)

    except KeyboardInterrupt:
        pass
    finally:
        if len(deck.blocks) > 0:
            filename = make_output_filename()
            update_line('Saving {}'.format(filename))
            audio.save(filename, deck.blocks)
        else:
            update_line('Nothing to save')
        print()


main()
