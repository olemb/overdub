import meep
from .threads import start_thread


def _is_connected():
    for name in meep.list_inputs():
        if 'microkey' in name.lower():
            return True
    else:
        return False


def start(deck):
    def handle_pedal():
        port = meep.open_input('microkey')

        for msg in port:
            if msg.is_cc(64):
                if msg.value == 127:
                    deck.punch_in()
                elif msg.value == 0:
                    deck.punch_out()

    if _is_connected():
        return start_thread(handle_pedal)
    else:
        return None
