"""Read from /dev/input/js0 and return as dictionaries.

Init:

                  8 = init?
Time stamp        |
(ms since boot)   |
--+--+--+--       |  -- Button number
f0 fb 37 09 00 00 81 00
f0 fb 37 09 00 00 81 01
f0 fb 37 09 00 00 81 02
f0 fb 37 09 00 00 81 03
f0 fb 37 09 00 00 81 04
f0 fb 37 09 00 00 81 05
f0 fb 37 09 00 00 81 06
f0 fb 37 09 00 00 81 07
f0 fb 37 09 00 00 81 08
f0 fb 37 09 00 00 81 09
f0 fb 37 09 00 00 81 0a
f0 fb 37 09 00 00 81 0b
f0 fb 37 09 00 00 82 00
f0 fb 37 09 00 00 82 01
f0 fb 37 09 00 00 82 02
f0 fb 37 09 00 00 82 03
f0 fb 37 09 00 00 82 04
f0 fb 37 09 00 00 82 05
            --+--  |
              |    1 = button, 2 = 
              |
            value (little endian unsigned)

        button down
             |
98 f0 2f 09 01 00 01 00   1 down
08 fa 2f 09 00 00 01 00   1 up

2c 6a 31 09 01 00 01 01   2 down
04 73 31 09 00 00 01 01   2 up

48 bf 32 09 01 00 01 02   3 down
f8 c4 32 09 00 00 01 02   3 up


Logitech PS2-style gamepad:

   axis 0 == left stick   -left / right   (left is negative)
   axis 1 == left stick   -up / down      (up is negative)
   axis 2 == right stick  -left / right
   axis 3 == right stick  -up / down
   axis 4 == plus stick   -left / right   (when mode is off), values min/0/max
   axis 5 == plus stick   -up / down      (when mode is off, values min/0/max

The + stick has two modes. When the mode light is off, it sends axis
4/5. When mode is on, it sends axis 0/1. The values are -32767, 0, and 32767.

Other axis have values from -32767 to 32767 as well.

"""
import queue
import struct
import threading

JS_EVENT_BUTTON = 0x1
JS_EVENT_AXIS = 0x2
JS_EVENT_INIT = 0x80

EVENT_SIZE = 8


def normalize_value(value):
    """Normalize value to -1..1."""
    return float(value) / 0x7fff


def unpack_event(data):
    raw = {}
    (raw['timestamp'],
     raw['value'],
     raw['type'],
     raw['number']) = struct.unpack('IhBB', data)

    event = {}
    event['init'] = bool(raw['type'] & 0x80)
    event['type'] = {1: 'button', 2: 'axis'}[raw['type'] & 0x7f]
    event['number'] = raw['number']
    event['raw_value'] = raw['value']
    event['timestamp'] = raw['timestamp']

    if event['type'] == 'axis':
        event['value'] = normalize_value(raw['value'])
    else:
        event['value'] = bool(raw['value'])

    return event


def read_event(device):
    return unpack_event(device.read(EVENT_SIZE))


class Joystick:
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

    js = Joystick(number=0, optional=True)

    while True:
        print(js.events)
        time.sleep(0.1)
