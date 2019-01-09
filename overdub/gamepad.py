import os
import struct
from dataclasses import dataclass


@dataclass(frozen=True)
class GamepadEvent:
    type: str
    number: int
    value: (float, bool)  # Hmm...
    is_init: bool
    raw_value: int
    timestamp: int

    def is_axis(self, number=None):
        if self.type != 'axis':
            return False
        elif number is not None and self.number != number:
            return False
        else:
            return True

    def is_button(self, number=None):
        if self.type != 'button':
            return False
        elif number is not None and self.number != number:
            return False
        else:
            return True

    def is_button_press(self, number=None):
        return self.is_button(number) and self.value == True


def normalize_value(value):
    """Normalize value to -1..1."""
    return float(value) / 0x7fff


def parse_event(data):
    timestamp, raw_value, event_type, number = struct.unpack('IhBB', data)
    
    type_str = {1: 'button', 2: 'axis'}[event_type & 0x7f]

    if type_str == 'axis':
        value = normalize_value(raw_value)
    else:
        value = bool(raw_value)

    return GamepadEvent(is_init=bool(event_type & 0x80),
                        type=type_str,
                        number=number,
                        value=value,
                        raw_value=raw_value,
                        timestamp=timestamp)


def read_event(device):
    event_size = 8
    return parse_event(device.read(event_size))


def gamepad_exists(number):
    return os.path.exists(f'/dev/input/js{number}')


def list_gamepads():
    return [i for i in range(16) if gamepad_exists(i)]


def iter_gamepad(number, include_init=False):
    if not (isinstance(number, int) and number >= 0):
        raise ValueError('gamepad number must be positive integer')

    with open(f'/dev/input/js{number}', 'rb') as infile:
        while True:
            event = read_event(infile)
            if event.is_init:
                if include_init:
                    yield event
            else:
                yield event
