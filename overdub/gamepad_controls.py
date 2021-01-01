from .gamepad import iter_gamepad, gamepad_exists
from .threads import start_thread


def start(deck):
    def handle_gamepad():
        for event in iter_gamepad(0):
            if event.is_button_press(0):
                deck.record()
            elif event.is_button_press(1):
                deck.stop()
            elif event.is_button_press(2):
                deck.play()
            elif event.is_button_press(3):
                deck.goto(0)
            elif event.is_axis(3):
                deck.scrub(event.value * -100)

    if gamepad_exists(0):
        return start_thread(handle_gamepad)
    else:
        return None
