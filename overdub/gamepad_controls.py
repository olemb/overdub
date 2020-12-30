from .gamepad import iter_gamepad, gamepad_exists
from .threads import start_thread
from .commands import Goto, Scrub, Record, Play, Stop


def start(do):
    def handle_gamepad():
        for event in iter_gamepad(0):
            if event.is_button_press(0):
                do(Record())
            elif event.is_button_press(1):
                do(Stop())
            elif event.is_button_press(2):
                do(Play())
            elif event.is_button_press(3):
                do(Goto(0))
            elif event.is_axis(3):
                do(Scrub((-event.value) * 100))

    if gamepad_exists(0):
        return start_thread(handle_gamepad)
    else:
        return None
