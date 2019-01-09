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
    if _is_connected():
        port = meep.open_input('microkey')
        
        def handle_input():
            for msg in port:
                if msg.is_cc(64):
                    if msg.value == 127:
                        do(PunchIn())
                    elif msg.value == 0:
                        do(PunchOut())

        return start_thread(handle_input)
    else:
        return None
