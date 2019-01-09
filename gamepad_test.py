import os
import sys
import time
from overdub.status_line import format_status
from overdub.threads import start_thread
from overdub.gamepad import iter_gamepad
from overdub.deck import Deck
from overdub.commands import Goto, Scrub, Record, Play, Stop
from overdub.terminal_ui import hidden_cursor

deck = Deck()
filename = sys.argv[1]

if os.path.exists(filename):
    deck.load(filename)


def handle_gamepad():
    for event in iter_gamepad(0):
        if event.is_button(0, True):
            deck.do(Record())
        elif event.is_button(1, True):
            deck.do(Stop())
        elif event.is_button(2, True):
            deck.do(Play())
        elif event.is_button(3, True):
            deck.do(Goto(0))
        elif event.is_axis(3):
            deck.do(Scrub((-event.value) * 100))


def display():
    with hidden_cursor():
        while True:
            print('\r' + format_status(deck.get_status()), end='', flush=True)
            time.sleep(0.1)


try:
    start_thread(handle_gamepad)
    display()
except KeyboardInterrupt:
    deck.save(filename)

