from .gamepad import iter_gamepad, gamepad_exists
from .threads import start_thread
from .commands import Record, Stop, Play, Goto, Scrub

def start_gamepad(do):
    def handle_gamepad():
        for event in iter_gamepad(0):
            if event.is_button(0, True):
                do(Record())
            elif event.is_button(1, True):
                do(Stop())
            elif event.is_button(2, True):
                do(Play())
            elif event.is_button(3, True):
                do(Goto(0))
            elif event.is_axis(3):
                do(Scrub((-event.value) * 100))

    if gamepad_exists(0):
        return start_thread(handle_gamepad)
    else:
        return None
