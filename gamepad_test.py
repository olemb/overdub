import sys
import time
from overdub.status_line import format_status
from overdub.threads import start_thread
from overdub.gamepad import iter_gamepad
from overdub.deck import Deck
from overdub.commands import Record, Play, Stop, Scrub


deck = Deck()

if sys.argv[1:]:
    deck.load(sys.argv[1])


def handle_gamepad():
    for event in iter_gamepad(0):
        if event.is_button(0, True):
            deck.do(Record())
        elif event.is_button(1, True):
            deck.do(Stop())
        elif event.is_button(2, True):
            deck.do(Play())
        elif event.is_axis(3):
            deck.do(Scrub((-event.value) * 100))


def update_display():
    while True:
        print('\r' + format_status(deck.get_status()), end='', flush=True)
        time.sleep(0.1)


start_thread(handle_gamepad)
update_display()
