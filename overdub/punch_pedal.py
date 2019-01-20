import meep
from .commands import PunchIn, PunchOut
from .threads import start_thread


def _is_connected():
    for name in meep.list_inputs():
        if 'microkey' in name.lower():
            return True
    else:
        return False


def start(do):
    def handle_pedal():
        port = meep.open_input('microkey')

        for msg in port:
            if msg.is_cc(64):
                if msg.value == 127:
                    do(PunchIn())
                elif msg.value == 0:
                    do(PunchOut())

    if _is_connected():        
        return start_thread(handle_pedal)
    else:
        return None
