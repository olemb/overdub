import os
import sys
import time
import fcntl
import termios
from contextlib import contextmanager
from . import audio
from .status_line import format_status
from .commands import TogglePlay, ToggleRecord, Skip
from .deck import Deck


def hide_cursor():
    print('\033[?25l', end='', flush=True)


def show_cursor():
    print('\033[?25h', end='', flush=True)


@contextmanager
def hidden_cursor():
    hide_cursor()
    try:
        yield
    finally:
        show_cursor()


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


def make_minimalist_status_line(status):
    # This produces some broken characters around the colored text.
    # if status.mode == 'recording':
    #     mode = color_text('recording', 'red')
    # elif status.mode == 'playing':
    #     mode = color_text('playing', 'green')
    # else:
    #     mode = status.mode
    mode = status.mode

    if status.time < 0.1:
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

    return f' {dot} {mode}'


def get_event():
    char = sys.stdin.read(1)

    if char == '\x1b':
        code = sys.stdin.read(2)
        if code == '[C':
            return 'wind'
        elif code == '[D':
            return 'rewind'
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


def ui(filename, minimalist=False):
    deck = Deck()

    if os.path.exists(filename):
        deck.load(filename)

    try:
        with term():
            while True:
                for event in get_events():
                    if event == 'quit':
                        return
                    elif event == 'snapshot':
                        update_line(f'Saving {filename}')
                        print()
                        deck.save(filename)
                    elif event == 'toggle_play':
                        deck.do(TogglePlay())
                    elif event == 'toggle_record':
                        deck.do(ToggleRecord())
                    elif event == 'wind':
                        deck.do(Skip(1))
                    elif event == 'rewind':
                        deck.do(Skip(-1))

                status = deck.get_status()
                if minimalist:
                    update_line(make_minimalist_status_line(status))
                else:
                    update_line('  ' + format_status(status))

                time.sleep(0.05)

    except KeyboardInterrupt:
        pass
    finally:
        if len(deck.blocks) > 0:
            update_line(f'Saving {filename}')
            deck.save(filename)
        else:
            update_line('Nothing to save')
        print()
