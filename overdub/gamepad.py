"""Read from /dev/input/js0 and return as dictionaries.
"""
import queue
import struct
import threading

JS_EVENT_BUTTON = 1
JS_EVENT_AXIS = 2

EVENT_SIZE = 8


def normalize_value(value):
    """Normalize value to -1..1."""
    return float(value) / 0x7fff


def unpack_event(data):
    raw = {}
    (raw['timestamp'],
     raw['value'],
     raw['type'],
     raw['code']) = struct.unpack('IhBB', data)

    event = {}
    event['init'] = bool(raw['type'] & 0x80)
    event['type'] = {1: 'button', 2: 'axis'}[raw['type'] & 0x7f]
    event['code'] = raw['code']
    event['raw_value'] = raw['value']
    event['timestamp'] = raw['timestamp']

    if event['type'] == 'axis':
        event['value'] = normalize_value(raw['value'])
    else:
        event['value'] = bool(raw['value'])

    return event


def read_event(device):
    return unpack_event(device.read(EVENT_SIZE))


class Gamepad:
    def __init__(self, number=0, optional=False, callback=None):
        self.number = number
        self.path = '/dev/input/js{}'.format(number)
        self._queue = queue.Queue()
        self._callback = callback
        
        try:
            self._file = open(self.path, 'rb')
            self.found = True
        except FileNotFoundError:
            self.found = False
            if optional:
                return
            else:
                raise

        self._thread = threading.Thread(target=self._mainloop)
        self._thread.setDaemon(True)
        self._thread.start()

    def _mainloop(self):
        while True:
            event = read_event(self._file)
            if self._callback:
                self._callback(event)
            else:
                self._queue.put(event)

    @property
    def events(self):
        events = []

        while True:
            try:
                events.append(self._queue.get_nowait())
            except queue.Empty:
                return events

    def get(self):
        return self._queue.get()

    def poll(self):
        try:
            return self.get()
        except queue.Empty:
            return None

    def __iter__(self):
        while True:
            yield self.get()


if __name__ == '__main__':
    import time

    js = Gamepad(number=0, optional=True)

    while True:
        print(js.events)
        time.sleep(0.1)
